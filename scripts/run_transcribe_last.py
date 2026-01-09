import os
import sys
import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_harvest.settings')
django.setup()

from harvest.models import DailyRecord
from harvest.stt import transcribe_and_append_text_from_audio


def run_for_last():
    r = DailyRecord.objects.order_by('-created_at').first()
    if not r:
        print('No DailyRecord found')
        return
    print('Running transcription for record pk=', r.pk, 'audio=', getattr(r.audio, 'path', None))
    try:
        res = transcribe_and_append_text_from_audio(r)
        print('transcribe returned:', res)
    except Exception as e:
        print('transcribe raised exception:', e)


if __name__ == '__main__':
    run_for_last()
