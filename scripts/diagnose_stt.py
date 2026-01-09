import os
import sys
import django
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_harvest.settings')
django.setup()

from harvest.models import DailyRecord
from harvest import stt


def diagnose_for_last():
    print('ENV BAIDU_API_KEY:', os.getenv('BAIDU_API_KEY'))
    print('ENV BAIDU_SECRET_KEY:', os.getenv('BAIDU_SECRET_KEY'))
    print('settings attr BAIDU_API_KEY:', getattr(stt, 'settings', None) and getattr(stt.settings, 'BAIDU_API_KEY', None))

    r = DailyRecord.objects.order_by('-created_at').first()
    if not r:
        print('No DailyRecord found')
        return
    print('Record pk=', r.pk, 'audio=', getattr(r.audio, 'path', None))
    audio_path = getattr(r.audio, 'path', None)
    if not audio_path or not os.path.exists(audio_path):
        print('Audio file missing or not found on disk')
        return

    try:
        wav = stt._ensure_wav_16k_mono(audio_path)
        print('Converted wav:', wav)
    except Exception:
        print('Failed to convert to wav:')
        traceback.print_exc()
        return

    try:
        token = stt._baidu_get_token(os.getenv('BAIDU_API_KEY'), os.getenv('BAIDU_SECRET_KEY'))
        print('Token obtained:', token[:8] + '...' if token else token)
    except Exception:
        print('Failed to get token:')
        traceback.print_exc()
        return

    try:
        resp = stt._baidu_asr(wav, token)
        print('ASR response:', resp)
    except Exception:
        print('ASR request failed:')
        traceback.print_exc()
        return


if __name__ == '__main__':
    diagnose_for_last()
