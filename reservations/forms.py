from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name']
        labels = {
            'name': '予約者名',
        }
        widgets ={
            'name': forms.TextInput(attrs={
                'placeholder': '予約者名',
            }),
        }
