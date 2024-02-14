from datetime import date
from django.forms.widgets import TextInput,Textarea,Select,EmailInput
from django import forms

from . models import *
        
class ExportingCountryForm(forms.ModelForm):

    class Meta:
        model = ExportingCountry
        fields = ['country_name','cash_type']

        widgets = {
            'country_name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Country Name'}), 
            'cash_type': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Cash Type'}), 
        }
        
class CourierPartnerForm(forms.ModelForm):

    class Meta:
        model = CourierPartner
        fields = ['name','contact_person','email','phone_number','address','website','services_offered','tracking_url','remarks']

        widgets = {
            'name': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Name'}), 
            'contact_person': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Contact Person'}), 
            'email': EmailInput(attrs={'class': 'required form-control','placeholder' : 'Enter Email'}), 
            'phone_number': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Phone Number'}), 
            'address': Textarea(attrs={'class': 'required form-control','placeholder' : 'Enter Address'}), 
            'website': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Website'}), 
            'services_offered': Textarea(attrs={'class': 'required form-control','placeholder' : 'Enter Services Offered'}), 
            'tracking_url': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter Tracking url'}), 
            'remarks': Textarea(attrs={'class': 'required form-control','placeholder' : 'Enter Remark'}), 
        }

class ExportingForm(forms.ModelForm):
    
    class Meta:
        model = Exporting
        fields = ['date','exporting_country','courier_partner']
        
        widgets = {
            'exporting_country': Select(attrs={'class': 'required form-control'}), 
            'courier_partner': Select(attrs={'class': 'required form-control'}), 
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['date'].widget = forms.TextInput(attrs={
            'type': 'date',
            'class': 'required form-control',
            'placeholder': 'Enter Date',
            'value': date.today().strftime('%Y-%m-%d')
        })
        
        
class ExportingItemsForm(forms.ModelForm):
    
    class Meta:
        model = ExportItem
        fields = ['per_kg_amount','qty','amount','purchasestock']

        widgets = {
            'per_kg_amount': TextInput(attrs={'class': 'required form-control amount_per_kg','placeholder' : 'Enter pe kg Amount'}), 
            'qty': TextInput(attrs={'type':'number','class': 'required form-control','placeholder' : 'Enter QTY'}), 
            'amount': TextInput(attrs={'type':'number','class': 'form-control','placeholder' : 'Enter Amount'}), 
            'purchasestock': Select(attrs={'class': 'required form-control'}),
        }

class ExportingExpenseForm(forms.ModelForm):
    
    class Meta:
        model = ExportExpense
        fields = ['title','amount']

        widgets = {
            'title': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter title'}), 
            'amount': TextInput(attrs={'type':'number','class': 'required form-control','placeholder' : 'Enter Amount'}), 
        }
        
        
class ExportingStatusForm(forms.ModelForm):
    
    class Meta:
        model = ExportStatus
        fields = ['status']

        widgets = {
            'status': Select(attrs={'class': 'required form-control'}), 
        }
