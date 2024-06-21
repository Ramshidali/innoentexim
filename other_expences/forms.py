from django.forms.widgets import TextInput,Textarea,Select
from django import forms
from . models import *

class ExpenceTypesForm(forms.ModelForm):

    class Meta:
        model = ExpenceTypes
        fields = ['name','description']

        widgets = {
            'name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Name'}),
            'description': Textarea(attrs={'class': 'form-control text-area','placeholder' : 'Enter Description','rows':'2'}), 
        }
        
        
class OtherExpencesForm(forms.ModelForm):

    class Meta:
        model = OtherExpences
        fields = ['remark','expence_type','country_rate','country']

        widgets = {
            'remark': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Remark'}),
            'country_rate': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Amount'}),
            'expence_type': Select(attrs={'class': 'required form-control'}), 
            'country': Select(attrs={'class': 'required form-control'}), 
        }
    