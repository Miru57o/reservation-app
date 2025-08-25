# reservations/views.py
from django.shortcuts import render, redirect, get_object_or_404 # redirect, get_object_or_404 は他で使用
from django.http import JsonResponse
from django.urls import reverse # リダイレクト用
from django.utils import timezone # timezone.now() のために
from .models import Booking
from .forms import BookingForm # booking_form_view で使用
from datetime import date, timedelta, datetime, time # datetime, time を追加
import json # json.dumps のために

# 予約可能な時間帯リスト (プロジェクト設定やDBから取得する方が柔軟性が高い)
AVAILABLE_TIME_SLOTS = ["09:00", "10:00", "11:00", "12:00","13:00", "14:00", "15:00", "16:00","17:00", "18:00", "19:00"]

def calendar_page_view(request): # 関数名を変更 (旧 calendar_view)
    """FullCalendarをホストするページをレンダリングするビュー"""
    context = {
        'available_time_slots_json': json.dumps(AVAILABLE_TIME_SLOTS),
        'today_iso': timezone.now().date().isoformat(), # YYYY-MM-DD 形式
    }
    return render(request, 'reservations/calendar.html', context)

def bookings_json_view(request): # 関数名を変更 (旧 bookings_json)
    """FullCalendar用の予約データをJSONで返すビュー"""
    start_str = request.GET.get('start', '').split('T')[0] # YYYY-MM-DD
    end_str = request.GET.get('end', '').split('T')[0]     # YYYY-MM-DD

    bookings_query = Booking.objects.all()
    if start_str:
        bookings_query = bookings_query.filter(date__gte=start_str)
    if end_str:
        # FullCalendarのendはexclusiveなので、LTEで良いか確認 (通常は<)
        # しかし、dateフィールドのみなので、その日の終わりまで含むとしておく
        bookings_query = bookings_query.filter(date__lte=end_str)

    events = []
    for booking in bookings_query:
        try:
            hour, minute = map(int, booking.time_slot.split(':'))
            # datetimeオブジェクトを正しく作成
            start_datetime = datetime.combine(booking.date, time(hour, minute))
            # 終了時刻を仮に1時間後とする (実際の運用に合わせて調整)
            end_datetime = start_datetime + timedelta(hours=1)

            events.append({
                'title': f"{booking.name}様", # イベントのタイトルに予約者名を表示
                'start': start_datetime.isoformat(), # ISO 8601形式
                'end': end_datetime.isoformat(),     # ISO 8601形式
                # 'allDay': False, # 時間指定があるのでallDayではない
                'id': booking.pk, # 予約ID
                'extendedProps': { # カスタムプロパティ
                    'time_slot': booking.time_slot,
                    # 必要であれば他の情報も追加
                }
            })
        except ValueError:
            # time_slotの形式が不正な場合はスキップ（エラーログ推奨）
            print(f"Skipping booking with invalid time_slot: {booking.id}")
            pass
            
    return JsonResponse(events, safe=False)

def book_slot_view(request, year, month, day, time_slot_str):
    try:
        target_date = date(int(year), int(month), int(day))
    except ValueError:
        # 不正な日付の場合はカレンダーにリダイレクト
        return redirect('reservations:calendar_default')

    # time_slot_strが "10:00" のような形式であることを確認 (簡易的)
    if not (len(time_slot_str) == 5 and time_slot_str[2] == ':' and time_slot_str.replace(':', '').isdigit()):
        return redirect('reservations:calendar_default') # 不正な時間ならリダイレクト

    # 過去の日付や時間は予約不可
    current_dt = timezone.now()
    try:
        target_hour, target_minute = map(int, time_slot_str.split(':'))
        target_datetime = timezone.make_aware(datetime(target_date.year, target_date.month, target_date.day, target_hour, target_minute))
        if target_datetime < current_dt:
            # メッセージフレームワークを使ってエラー表示する方が親切
            return render(request, 'reservations/booking_error.html', {'message': '過去の日時は予約できません。'})
    except ValueError:
        return redirect('reservations:calendar_default') # 時間文字列が不正


    # 既に予約されていないか確認
    if Booking.objects.filter(date=target_date, time_slot=time_slot_str).exists():
        # メッセージフレームワークを使ってエラー表示する方が親切
        return render(request, 'reservations/booking_error.html', {'message': 'この時間帯は既に予約されています。'})


    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.date = target_date
            booking.time_slot = time_slot_str
            try:
                booking.save()
                # 予約完了ページなどへリダイレクト
                return redirect(reverse('reservations:booking_complete', kwargs={'pk': booking.pk}))
            except Exception as e: # 例えばunique_together制約違反など
                form.add_error(None, f"予約の保存に失敗しました。{e}")

    else: # GETリクエストの場合
        form = BookingForm()

    context = {
        'form': form,
        'year': year,
        'month': month,
        'day': day,
        'time_slot_str': time_slot_str,
        'page_title': f"{year}年{month}月{day}日 {time_slot_str} の予約"
    }
    return render(request, 'reservations/booking_form.html', context)

def booking_complete_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    context = {
        'booking': booking,
        'page_title': '予約完了'
    }
    return render(request, 'reservations/booking_complete.html', context)