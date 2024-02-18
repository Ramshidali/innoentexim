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
            'purchasestock': Select(attrs={'class': 'required form-control purchase-item','style':'width: auto;'}),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        if instance:
            self.fields['purchasestock'].queryset = PurchaseStock.objects.filter(pk=instance.pk)
        else:
            # valid_purchase_items = PurchaseStock.objects.filter(qty__gt=0).values_list('purchasestock', flat=True)
            self.fields['purchasestock'].queryset = PurchaseStock.objects.filter(qty__gt=0)
            
    def clean(self):
        cleaned_data = super().clean()
        purchasestock = cleaned_data.get('purchasestock')
        input_qty = cleaned_data.get('qty')
        
        instance = getattr(self, 'instance', None)
        
        stock_qty = PurchaseStock.objects.get(pk=purchasestock.pk,is_deleted=False).qty
        
        if instance.qty :
            if not instance.qty == input_qty:
                available_stock_include_input = stock_qty + input_qty
                if not available_stock_include_input > input_qty:
                    pass
                else:
                    error_message = f"Qty: No stock available in {purchasestock.purchase_item.name}, only {stock_qty} left"
                raise forms.ValidationError(error_message)
            else:
                pass
        else:
            if purchasestock is not None and stock_qty < input_qty:
                if stock_qty <= 0:
                    error_message = f"Qty: No stock available in {purchasestock.purchase_item.name}"
                else:
                    error_message = f"Qty: No stock available in {purchasestock.purchase_item.name}, only {stock_qty} left"
                raise forms.ValidationError(error_message)

        return cleaned_data

class ExportingExpenseForm(forms.ModelForm):
    
    class Meta:
        model = ExportExpense
        fields = ['title','amount']

        widgets = {
            'title': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter title'}), 
            'amount': TextInput(attrs={'type':'number','class': 'required form-control','placeholder' : 'Enter Amount'}), 
        }
        
        
class ExportingStatusForm(forms.ModelForm):
    export_id = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden','name': 'export_id','id':'exportIdModalField'}))
    
    class Meta:
        model = ExportStatus
        fields = ['status','caption','export_id']

        widgets = {
            'status': Select(attrs={'class': 'required form-control'}), 
            'caption': Textarea(attrs={'class': 'required form-control','placeholder' : 'Enter Caption','rows':'3'}), 
        }
