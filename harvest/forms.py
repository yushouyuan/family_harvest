from django import forms
from .models import DailyRecord
from datetime import date


class DailyRecordForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        required=True,
    )

    class Meta:
        model = DailyRecord
        fields = ['date', 'text', 'audio']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        # ensure initial contains today's date for new records only
        kwargs.setdefault('initial', {})
        instance = kwargs.get('instance', None)
        if not instance or not getattr(instance, 'pk', None):
            kwargs['initial'].setdefault('date', date.today())
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        text = cleaned.get('text', '').strip()
        audio = cleaned.get('audio')
        if not text and not audio:
            raise forms.ValidationError('请填写文字或上传语音。')
        return cleaned
