# reservations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST # POSTのみ受け付けるデコレータ
from .models import Booking, Schedule # Scheduleモデルをインポート
from .forms import BookingForm
from datetime import date, timedelta, datetime, time
import json

# 予約可能な時間帯リスト
AVAILABLE_TIME_SLOTS = ["09:00", "10:00", "11:00", "12:00","13:00", "14:00", "15:00", "16:00","17:00", "18:00", "19:00"]

def calendar_page_view(request):
    """FullCalendarをホストするページをレンダリングするビュー"""
    context = {
        'available_time_slots_json': json.dumps(AVAILABLE_TIME_SLOTS),
        'today_iso': timezone.now().date().isoformat(),
    }
    return render(request, 'reservations/calendar.html', context)

def bookings_json_view(request):
    """FullCalendar用の予約・スケジュールデータをJSONで返すビュー"""
    start_str = request.GET.get('start', '').split('T')[0]
    end_str = request.GET.get('end', '').split('T')[0]
    
    events = []

    # 予約データを取得
    bookings_query = Booking.objects.all()
    if start_str:
        bookings_query = bookings_query.filter(date__gte=start_str)
    if end_str:
        bookings_query = bookings_query.filter(date__lte=end_str)

    for booking in bookings_query:
        try:
            hour, minute = map(int, booking.time_slot.split(':'))
            start_datetime = datetime.combine(booking.date, time(hour, minute))
            end_datetime = start_datetime + timedelta(hours=1)
            events.append({
                'title': f"{booking.name}様",
                'start': start_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'id': booking.pk,
                'extendedProps': {
                    'type': 'booking', # 種別を追加
                    'time_slot': booking.time_slot,
                }
            })
        except ValueError:
            print(f"Skipping booking with invalid time_slot: {booking.id}")
            pass

    # 全体スケジュールデータを取得
    schedules_query = Schedule.objects.all()
    if start_str:
        schedules_query = schedules_query.filter(date__gte=start_str)
    if end_str:
        schedules_query = schedules_query.filter(date__lte=end_str)

    for schedule in schedules_query:
        events.append({
            'title': schedule.title,
            'start': schedule.date.isoformat(), # 終日イベント
            'allDay': True,
            'id': schedule.pk,
            'backgroundColor': '#6c757d', # イベントの背景色
            'borderColor': '#6c757d',   # イベントの枠線の色
            'extendedProps': {
                'type': 'schedule', # 種別を追加
            }
        })
            
    return JsonResponse(events, safe=False)

def book_slot_view(request, year, month, day, time_slot_str):
    try:
        target_date = date(int(year), int(month), int(day))
    except ValueError:
        return redirect('reservations:calendar_page')

    if not (len(time_slot_str) == 5 and time_slot_str[2] == ':' and time_slot_str.replace(':', '').isdigit()):
        return redirect('reservations:calendar_page')

    current_dt = timezone.now()
    try:
        target_hour, target_minute = map(int, time_slot_str.split(':'))
        target_datetime = timezone.make_aware(datetime(target_date.year, target_date.month, target_date.day, target_hour, target_minute))
        if target_datetime < current_dt:
            return render(request, 'reservations/booking_error.html', {'message': '過去の日時は予約できません。'})
    except ValueError:
        return redirect('reservations:calendar_page')

    if Booking.objects.filter(date=target_date, time_slot=time_slot_str).exists():
        return render(request, 'reservations/booking_error.html', {'message': 'この時間帯は既に予約されています。'})

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.date = target_date
            booking.time_slot = time_slot_str
            try:
                booking.save()
                return redirect(reverse('reservations:booking_complete', kwargs={'pk': booking.pk}))
            except Exception as e:
                form.add_error(None, f"予約の保存に失敗しました。{e}")
    else:
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

@require_POST # このビューはPOSTリクエストのみを受け付けます
def delete_booking_view(request, pk):
    """予約を削除するビュー"""
    try:
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        return JsonResponse({'status': 'success', 'message': '予約を削除しました。'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)