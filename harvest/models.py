from django.db import models


class FamilyMember(models.Model):
    username = models.CharField(max_length=32, unique=True)
    display_name = models.CharField(max_length=64)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.display_name


class DailyRecord(models.Model):
    member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='records')
    date = models.DateField()
    text = models.TextField(blank=True)
    audio = models.FileField(upload_to='audio_records/', blank=True, null=True)
    # 存储已转写的音频文件哈希，避免对同一音频重复转写并追加文本
    audio_hash = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ('member', 'date')

    def __str__(self):
        return f"{self.member} @ {self.date}"
