from datetime import date

from django.forms.widgets import TextInput,Textarea,Select,DateInput,CheckboxInput,FileInput,PasswordInput
from django import forms
from django.db.models import Sum

from dal import autocomplete

from sales.models import Sales, SalesStock, SalesItems, SalesExpenses


class SalesForm(forms.ModelForm):
    
    class Meta:
        model = Sales
        fields = ['date','sales_party','country']
        
        widgets = {        
            'country': Select(attrs={'class': 'select2 form-control custom-select'}),
            'sales_party': Select(attrs={'class': 'select2 form-control custom-select','placeholder' : 'Select Sales Party'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = forms.TextInput(attrs={
            'type': 'date',
            'class': 'required form-control',
            'placeholder': 'Enter Date',
            'value': date.today().strftime('%Y-%m-%d')
        })


class SalesItemsForm(forms.ModelForm):
    
    class Meta:
        model = SalesItems
        fields = ['sales_stock','qty','per_kg_amount','amount']

        widgets = {
            'sales_stock': Select(attrs={'class': 'required form-control sales-item','style':'width: auto;'}), 
            'qty': TextInput(attrs={'type':'number','class': 'required form-control','placeholder' : 'Enter QTY'}), 
            'per_kg_amount': TextInput(attrs={'type':'number','class': 'required form-control amount_per_kg','placeholder' : 'Enter Amount per kg'}), 
            'amount': TextInput(attrs={'type':'number','class': 'required form-control','placeholder' : 'Enter Amount'}), 
        }
        
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        if instance:
            self.fields['sales_stock'].queryset = SalesStock.objects.filter(pk=instance.pk)
        else:
            # valid_purchase_items = SalesStock.objects.filter(qty__gt=0).values_list('sales_stock', flat=True)
            self.fields['sales_stock'].queryset = SalesStock.objects.filter(qty__gt=0)
            
    def clean(self):
        cleaned_data = super().clean()
        sales_stock = cleaned_data.get('sales_stock')
        input_qty = cleaned_data.get('qty')
        
        instance = getattr(self, 'instance', None)
        
        stock_qty = SalesStock.objects.get(pk=sales_stock.pk,is_deleted=False).qty
        
        if instance.qty :
            if not instance.qty == input_qty:
                available_stock_include_input = stock_qty + input_qty
                if not available_stock_include_input > input_qty:
                    pass
                else:
                    error_message = f"Qty: No stock available in {sales_stock.purchase_item.name}, only {stock_qty} left"
                raise forms.ValidationError(error_message)
            else:
                pass
        else:
            if sales_stock is not None and stock_qty < input_qty:
                if stock_qty <= 0:
                    error_message = f"Qty: No stock available in {sales_stock.purchase_item.name}"
                else:
                    error_message = f"Qty: No stock available in {sales_stock.purchase_item.name}, only {stock_qty} left"
                raise forms.ValidationError(error_message)

        return cleaned_data

class SalesExpenseForm(forms.ModelForm):
    
    class Meta:
        model = SalesExpenses
        fields = ['title','amount']

        widgets = {
            'title': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter title'}), 
            'amount': TextInput(attrs={'type':'number','class': 'required form-control','placeholder' : 'Enter Amount'}), 
        }