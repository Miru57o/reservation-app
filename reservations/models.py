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