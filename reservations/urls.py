from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'reservations'

urlpatterns = [
    # FullCalendarをホストするHTMLページをルートに
    path('', views.calendar_page_view, name='calendar_page'),
    # FullCalendarが予約データを取得するためのJSONエンドポイント
    path('api/bookings/', views.bookings_json_view, name='bookings_json'),
    # 既存の予約処理と完了ページのURL (変更なし)
    path('book/<int:year>/<int:month>/<int:day>/<str:time_slot_str>/', views.book_slot_view, name='book_slot'),
    path('booking_complete/<int:pk>/', views.booking_complete_view, name='booking_complete'),
    # 予約削除用のURL
    path('delete_booking/<int:pk>/', views.delete_booking_view, name='delete_booking'),
]