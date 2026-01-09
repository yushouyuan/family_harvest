from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FamilyMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, unique=True)),
                ('display_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='DailyRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('text', models.TextField(blank=True)),
                ('audio', models.FileField(blank=True, null=True, upload_to='audio_records/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='records', to='harvest.familymember')),
            ],
            options={
                'ordering': ['-date', '-created_at'],
                'unique_together': {('member', 'date')},
            },
        ),
    ]
