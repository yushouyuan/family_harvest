import os
import sys
import django
from datetime import date

# Ensure project root is on PYTHONPATH
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_harvest.settings')
django.setup()

from django.core.files import File
from harvest import stt as stt_module
from harvest.models import FamilyMember, DailyRecord


def make_silent_wav(path, duration_s=1, rate=16000):
    import wave
    n_frames = int(duration_s * rate)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b'\x00\x00' * n_frames)


def run_test():
    media_dir = os.path.join(os.getcwd(), 'media', 'audio_records')
    os.makedirs(media_dir, exist_ok=True)
    wav_path = os.path.join(media_dir, 'test_stt.wav')
    make_silent_wav(wav_path)

    member, _ = FamilyMember.objects.get_or_create(username='testuser', defaults={'display_name': '测试用户'})

    # Create record with initial text
    rec = DailyRecord(member=member, date=date.today(), text='原始文本')
    with open(wav_path, 'rb') as f:
        django_file = File(f)
        rec.audio.save('test_stt.wav', django_file, save=False)
    rec.save()

    # Monkeypatch BAIDU functions to return a fake successful result
    stt_module._baidu_get_token = lambda a, b: 'fake-token'
    def fake_asr(wav_path, token):
        return {'err_no': 0, 'result': ['这是模拟的转写文本']}
    stt_module._baidu_asr = fake_asr

    print('Calling transcribe_and_append_text_from_audio...')
    res = stt_module.transcribe_and_append_text_from_audio(rec)
    print('transcribe result:', res)

    # Refresh and print final text
    r2 = DailyRecord.objects.get(pk=rec.pk)
    print('final record.text:')
    print(r2.text)


if __name__ == '__main__':
    run_test()
