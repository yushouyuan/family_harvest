from django.core.management.base import BaseCommand
from harvest.models import FamilyMember

PRESET = [
    ('member1', '爸爸'),
    ('member2', '妈妈'),
    ('member3', '哥哥'),
    ('member4', '弟弟'),
]


class Command(BaseCommand):
    help = 'Create four preset family members'

    def handle(self, *args, **options):
        for username, display in PRESET:
            obj, created = FamilyMember.objects.get_or_create(username=username, defaults={'display_name': display})
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建: {display}'))
            else:
                self.stdout.write(f'已存在: {display}')
