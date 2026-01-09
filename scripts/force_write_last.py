import os
import sys
import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_harvest.settings')
django.setup()

from harvest.models import DailyRecord
from harvest import stt


def force_write():
    r = DailyRecord.objects.order_by('-created_at').first()
    if not r:
        print('No DailyRecord')
        return
    print('Record pk', r.pk, 'audio', getattr(r.audio, 'path', None))
    audio_path = getattr(r.audio, 'path', None)
    wav = stt._ensure_wav_16k_mono(audio_path)
    token = stt._baidu_get_token(os.getenv('BAIDU_API_KEY'), os.getenv('BAIDU_SECRET_KEY'))
    resp = stt._baidu_asr(wav, token)
    print('ASR resp:', resp)
    if resp.get('err_no') == 0 and resp.get('result'):
        recognized = ''.join(resp.get('result'))
        print('Recognized:', recognized)
        if r.text:
            r.text = r.text.rstrip() + '\n' + recognized
        else:
            r.text = recognized
        r.save(update_fields=['text'])
        print('Saved text to record', r.pk)


if __name__ == '__main__':
    force_write()
