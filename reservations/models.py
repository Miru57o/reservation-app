from django.db import models
from django.utils import timezone

class Booking(models.Model):
    name = models.CharField(max_length=100,verbose_name='予約者名')
    date = models.DateField(verbose_name='予約日')
    time_slot = models.CharField(max_length=5,verbose_name='予約時間帯')
    booked_at = models.DateTimeField(auto_now_add=True,verbose_name='予約日時')

    class Meta:
        verbose_name = '予約'
        verbose_name_plural = '予約一覧'
        unique_together = ('date', 'time_slot')

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} {self.time_slot} - {self.name}"
    
class Schedule(models.Model):
    """全体共有のスケジュールモデル"""
    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(blank=True, verbose_name='説明') 
    date= models.DateField(verbose_name='日付')

    class Meta:
        verbose_name = 'スケジュール'
        verbose_name_plural = 'スケジュール一覧'
        ordering = ['date']

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} - {self.title}"
