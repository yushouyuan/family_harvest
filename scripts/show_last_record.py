import os
import sys
import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_harvest.settings')
django.setup()

from harvest.models import DailyRecord


def show_last():
    r = DailyRecord.objects.select_related('member').order_by('-created_at').first()
    if not r:
        print('No DailyRecord found.')
        return
    print('PK:', r.pk)
    print('Member:', r.member.display_name)
    print('Date:', r.date)
    print('Audio field:', bool(r.audio), getattr(r.audio, 'url', ''))
    print('Text content:')
    print('---')
    print(r.text or '<empty>')
    print('---')


if __name__ == '__main__':
    show_last()
