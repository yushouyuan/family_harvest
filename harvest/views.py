from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from datetime import date

from .models import FamilyMember, DailyRecord
from django.db import IntegrityError
from .forms import DailyRecordForm
from .stt import transcribe_and_append_text_from_audio


def require_login(view):
    def _wrapped(request, *args, **kwargs):
        member_id = request.session.get('member_id')
        if not member_id:
            return redirect('login')
        request.member = get_object_or_404(FamilyMember, pk=member_id)
        return view(request, *args, **kwargs)
    return _wrapped


def login_view(request):
    members = FamilyMember.objects.all()
    if request.method == 'POST':
        mid = request.POST.get('member')
        if not mid:
            messages.error(request, '请选择一个成员')
        else:
            try:
                member = FamilyMember.objects.get(pk=int(mid))
                request.session['member_id'] = member.id
                # 同时保存显示名到 session，模板可直接使用
                request.session['member_name'] = member.display_name
                return redirect('index')
            except (FamilyMember.DoesNotExist, ValueError):
                messages.error(request, '选择无效')
    return render(request, 'harvest/login.html', {'members': members})


def logout_view(request):
    request.session.pop('member_id', None)
    request.session.pop('member_name', None)
    return redirect('login')


@require_login
def index(request):
    today = date.today()
    records = DailyRecord.objects.filter(date=today).select_related('member')
    members = FamilyMember.objects.all()
    # Prepare dict of member->record
    rec_map = {r.member_id: r for r in records}
    cards = []
    for m in members:
        cards.append({'member': m, 'record': rec_map.get(m.id)})
    context = {'cards': cards, 'today': today}
    return render(request, 'harvest/index.html', context)


@require_login
def add_or_edit_record(request, record_id=None):
    member = request.member
    instance = None
    if record_id:
        instance = get_object_or_404(DailyRecord, pk=record_id, member=member)

    if request.method == 'POST':
        form = DailyRecordForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            rec = form.save(commit=False)
            rec.member = member
            try:
                rec.save()
                # 转写音频并追加到 text（若配置了可用的 STT 提供者）
                try:
                    transcribe_and_append_text_from_audio(rec)
                except Exception:
                    # 转写失败不影响保存流程
                    pass
                messages.success(request, '保存成功')
                return redirect('index')
            except IntegrityError:
                # 已存在同日记录，改为更新已有记录
                existing = DailyRecord.objects.filter(member=member, date=rec.date).first()
                if existing:
                    existing.text = rec.text
                    if rec.audio:
                        existing.audio = rec.audio
                    existing.save()
                    # 更新后尝试转写并追加
                    try:
                        transcribe_and_append_text_from_audio(existing)
                    except Exception:
                        pass
                    messages.success(request, '已更新当天记录')
                    return redirect('index')
                else:
                    messages.error(request, '保存失败：唯一性冲突')
    else:
        if instance:
            form = DailyRecordForm(instance=instance)
        else:
            # pass ISO string so template/date input gets YYYY-MM-DD
            initial = {'date': date.today().isoformat()}
            form = DailyRecordForm(initial=initial)

    return render(request, 'harvest/record_form.html', {'form': form, 'member': member})


@require_login
def history(request):
    records = DailyRecord.objects.select_related('member').order_by('-date', '-created_at')
    return render(request, 'harvest/history.html', {'records': records})


@require_login
def stats(request):
    member = request.member
    total = DailyRecord.objects.filter(member=member).count()
    return render(request, 'harvest/stats.html', {'member': member, 'total': total})
