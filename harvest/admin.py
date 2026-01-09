from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv

from .models import FamilyMember, DailyRecord


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'display_name', 'avatar_tag', 'record_count')
    search_fields = ('username', 'display_name')

    def record_count(self, obj):
        return obj.records.count()
    record_count.short_description = '记录数'

    def avatar_tag(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="height:40px;border-radius:4px"/>', obj.avatar.url)
        return '-'
    avatar_tag.short_description = '头像'


@admin.register(DailyRecord)
class DailyRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'date', 'audio_player', 'created_at')
    list_filter = ('date', 'member')
    search_fields = ('text', 'member__display_name')
    readonly_fields = ('created_at',)
    raw_id_fields = ('member',)
    actions = ['export_as_csv']

    def audio_player(self, obj):
        if obj.audio:
            return format_html('<audio controls style="max-width:220px"><source src="{}" type="audio/webm">您的浏览器不支持 audio 标签</audio>', obj.audio.url)
        return '-'
    audio_player.short_description = '语音'

    def export_as_csv(self, request, queryset):
        """Admin action: export selected DailyRecord rows as CSV."""
        meta = self.model._meta
        field_names = ['id', 'member', 'date', 'text', 'audio', 'created_at']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=daily_records.csv'
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.member.display_name if obj.member else '',
                obj.date,
                (obj.text or '').replace('\n', '\\n'),
                obj.audio.url if obj.audio else '',
                obj.created_at,
            ])
        return response

    export_as_csv.short_description = '导出所选记录为 CSV'
