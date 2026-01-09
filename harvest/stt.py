import os
import tempfile
import base64
import requests
import subprocess
import logging
from django.conf import settings

logger = logging.getLogger('harvest.stt')


def _ensure_wav_16k_mono(src_path):
    """Convert audio file to WAV 16k mono using ffmpeg and return path."""
    fd, out_path = tempfile.mkstemp(suffix='.wav')
    os.close(fd)
    cmd = [
        'ffmpeg', '-y', '-i', src_path,
        '-ar', '16000', '-ac', '1', '-sample_fmt', 's16', out_path
    ]
    # Run ffmpeg; it must be available in PATH (Dockerfile installs it)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path


def _baidu_get_token(api_key, secret_key):
    token_url = 'https://aip.baidubce.com/oauth/2.0/token'
    params = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': secret_key,
    }
    r = requests.get(token_url, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get('access_token')


def _baidu_asr(wav_path, token):
    with open(wav_path, 'rb') as f:
        data = f.read()
    speech = base64.b64encode(data).decode('utf-8')
    url = 'https://vop.baidu.com/server_api'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'format': 'wav',
        'rate': 16000,
        'channel': 1,
        'cuid': 'family_harvest',
        'token': token,
        'speech': speech,
        'len': len(data),
    }
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def transcribe_and_append_text_from_audio(record):
    """Transcribe `record.audio` and append the recognized text to `record.text`.

    Requires BAIDU_API_KEY and BAIDU_SECRET_KEY configured in Django settings.
    If those are not present, the function is a no-op.
    """
    if not record or not record.audio:
        logger.debug('transcribe: no record or no audio present')
        return None

    audio_path = record.audio.path
    if not os.path.exists(audio_path):
        return None

    # 计算音频哈希，若与记录中已保存的 hash 相同，则视为音频未变化，跳过转写
    try:
        import hashlib
        h = hashlib.sha256()
        with open(audio_path, 'rb') as af:
            for chunk in iter(lambda: af.read(4096), b''):
                h.update(chunk)
        audio_sha = h.hexdigest()
    except Exception:
        audio_sha = None
    if audio_sha and getattr(record, 'audio_hash', None) == audio_sha:
        logger.info('Audio unchanged for record %s (hash=%s); skipping transcription', record.pk, audio_sha)
        return None

    api_key = getattr(settings, 'BAIDU_API_KEY', None) or os.getenv('BAIDU_API_KEY')
    secret_key = getattr(settings, 'BAIDU_SECRET_KEY', None) or os.getenv('BAIDU_SECRET_KEY')
    if not api_key or not secret_key:
        logger.info('BAIDU_API_KEY/BAIDU_SECRET_KEY not configured; skipping transcription')
        return None

    wav_path = None
    try:
        logger.info('Starting transcription for record pk=%s, audio=%s', record.pk, audio_path)
        wav_path = _ensure_wav_16k_mono(audio_path)
        logger.debug('Converted to wav: %s', wav_path)
        token = _baidu_get_token(api_key, secret_key)
        logger.debug('Obtained BAIDU token (len=%d)', len(token) if token else 0)
        resp = _baidu_asr(wav_path, token)
        logger.debug('BAIDU ASR response: %s', resp)
        # 解析返回
        if resp.get('err_no') == 0 and resp.get('result'):
            recognized = ''.join(resp.get('result'))
            logger.info('Recognized text for record %s: %s', record.pk, recognized)
            if recognized:
                # 追加到现有文本
                if record.text:
                    record.text = record.text.rstrip() + '\n' + recognized
                else:
                    record.text = recognized
                # 保存识别结果，仅更新 text 字段，并打印/记录确认（以便在开发服务器中可见）
                try:
                    # 先更新 text，再更新 audio_hash（若可用），避免覆盖其他字段
                    if audio_sha:
                        record.save(update_fields=['text', 'audio_hash'])
                        # 有些 Django 后端在 update_fields 上可能不接受两个字段同时更新，保险回退
                    else:
                        record.save(update_fields=['text'])
                except Exception:
                    # 退回到全量保存以防 update_fields 不可用
                    record.save()
                # 如果成功保存且有音频哈希，确保记录中保存该 hash（兼容回退路径）
                try:
                    if audio_sha and getattr(record, 'audio_hash', None) != audio_sha:
                        record.audio_hash = audio_sha
                        record.save(update_fields=['audio_hash'])
                except Exception:
                    try:
                        record.save()
                    except Exception:
                        pass
                msg = f"Transcription saved for record {record.pk}: {recognized}"
                try:
                    print(msg)
                except Exception:
                    pass
                logger.info(msg)
                return recognized
    finally:
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass
    return None
