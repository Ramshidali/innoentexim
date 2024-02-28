from datetime import date
from django.forms.widgets import TextInput,Textarea,Select,EmailInput
from django import forms

from . models import *

class ExchangeRateForm(forms.ModelForm):

    class Meta:
        model = ExchangeRate
        fields = ['country','currency','rate_to_inr','start_date','end_date']

        widgets = {
            'country': Select(attrs={'class': 'required form-control'}), 
            'currency': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Currency'}), 
            'rate_to_inr': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Rate to INR'}), 
            'start_date': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Rate to INR'}), 
            'end_date': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Rate to INR'}), 
        }