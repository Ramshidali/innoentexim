from datetime import date
from django.forms.widgets import TextInput,Textarea,Select,DateInput,CheckboxInput,FileInput,PasswordInput
from django import forms

from . models import *


class PurchaseItemForm(forms.ModelForm):
    
    class Meta:
        model = PurchaseItems
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Name'}), 
        }
        
        
class PurchaseForm(forms.ModelForm):
    
    class Meta:
        model = Purchase
        fields = ['date','purchase_party']
        
        widgets = {
            'purchase_party': Select(attrs={'class': 'required form-control'}), 
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['date'].widget = forms.TextInput(attrs={
            'type': 'date',
            'class': 'required form-control',
            'placeholder': 'Enter Date',
            'value': date.today().strftime('%Y-%m-%d')
        })
        
        
class PurchasedItemsForm(forms.ModelForm):
    
    class Meta:
        model = PurchasedItems
        fields = ['purchase_item','qty','amount']

        widgets = {
            'purchase_item': Select(attrs={'class': 'required form-control','placeholder' : 'Enter Items','style':'width: auto;'}),
            'qty': TextInput(attrs={'type':'number','class': 'required form-control','placeholder' : 'Enter QTY'}), 
            'amount': TextInput(attrs={'type':'number','class': 'form-control','placeholder' : 'Enter Amount'}), 
        }

class PurchaseExpenseForm(forms.ModelForm):
    
    class Meta:
        model = PurchaseExpense
        fields = ['title','amount']

        widgets = {
            'title': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter title'}), 
            'amount': TextInput(attrs={'type':'number','class': 'required form-control','placeholder' : 'Enter Amount'}), 
        }
