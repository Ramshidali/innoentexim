from datetime import date

from django.forms.widgets import TextInput,Textarea,Select,DateInput,CheckboxInput,FileInput,PasswordInput
from django import forms
from django.db.models import Sum

from dal import autocomplete

from sales.models import Damage, DamageItems, Sales, SalesStock, SalesItems, SalesExpenses


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
        fields = ['sales_stock','no_boxes','sale_type','qty','per_kg_amount','amount']
        widgets = {
            'sales_stock': forms.Select(attrs={'class': 'required form-control sales-item', 'style': 'width: auto;'}),
            'sale_type': forms.Select(attrs={'class': 'required form-control sales-type', 'style': 'width: auto;'}),
            'no_boxes': forms.TextInput(attrs={'type': 'number', 'class': 'form-control no_boxes', 'placeholder': 'Enter No.Boxes'}),
            'qty': forms.TextInput(attrs={'type': 'number', 'class': 'required form-control sales_qty', 'placeholder': 'Enter QTY'}),
            'per_kg_amount': forms.TextInput(attrs={'type': 'number', 'class': 'required form-control amount_per_kg', 'placeholder': 'Enter Amount per kg'}),
            'amount': forms.TextInput(attrs={'type': 'number', 'class': 'required form-control', 'placeholder': 'Enter Amount'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.fields['sales_stock'].queryset = SalesStock.objects.filter(qty__gt=0) | SalesStock.objects.filter(pk=instance.sales_stock.pk)
        else:
            self.fields['sales_stock'].queryset = SalesStock.objects.filter(qty__gt=0)
            
    def clean(self):
        cleaned_data = super().clean()
        sales_stock = cleaned_data.get('sales_stock')
        input_qty = cleaned_data.get('qty')
        sale_type = cleaned_data.get('sale_type')
        no_boxes = cleaned_data.get('no_boxes')
        
        instance = getattr(self, 'instance', None)
        
        # Check the stock quantity
        if sales_stock:
            stock_qty = SalesStock.objects.get(pk=sales_stock.pk, is_deleted=False).qty
            if instance and instance.qty:
                if instance.qty != input_qty:
                    available_stock_include_input = stock_qty + instance.qty
                    if not available_stock_include_input >= input_qty:
                        error_message = f"Qty: No stock available in {sales_stock.purchase_item.name}, only {stock_qty} left"
                        raise forms.ValidationError(error_message)
            else:
                if stock_qty < input_qty:
                    if stock_qty <= 0:
                        error_message = f"Qty: No stock available in {sales_stock.purchase_item.name}"
                    else:
                        error_message = f"Qty: No stock available in {sales_stock.purchase_item.name}, only {stock_qty} left"
                    raise forms.ValidationError(error_message)
        
        # Additional validation for no_boxes when sale_type is 'box'
        if sale_type == 'box':
            if no_boxes is None or no_boxes <= 0:
                error_message = "This field is required and must be greater than zero when sale type is 'box'."
                self.add_error('no_boxes', error_message)
        else:
            cleaned_data['no_boxes'] = None  # Ensure no_boxes is not required when sale_type is not 'box'
        
        return cleaned_data



class SalesExpenseForm(forms.ModelForm):
    
    class Meta:
        model = SalesExpenses
        fields = ['title','amount']

        widgets = {
            'title': TextInput(attrs={'class': 'required form-control','placeholder' : 'Enter title'}), 
            'amount': TextInput(attrs={'type':'number','class': 'required form-control','placeholder' : 'Enter Amount'}), 
        }
        
class DamageForm(forms.ModelForm):
    
    class Meta:
        model = Damage
        fields = ['date','country']
        
        widgets = {        
            'country': Select(attrs={'class': 'select2 form-control custom-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = forms.TextInput(attrs={
            'type': 'date',
            'class': 'required form-control',
            'placeholder': 'Enter Date',
            'value': date.today().strftime('%Y-%m-%d')
        })

class DamageItemsForm(forms.ModelForm):
    
    class Meta:
        model = DamageItems
        fields = ['stock_item','no_boxes','weight_type','qty']
        widgets = {
            'stock_item': forms.Select(attrs={'class': 'required form-control damage-item', 'style': 'width: auto;'}),
            'weight_type': forms.Select(attrs={'class': 'required form-control damage-type', 'style': 'width: auto;'}),
            'no_boxes': forms.TextInput(attrs={'type': 'number', 'class': 'form-control no_boxes', 'placeholder': 'Enter No.Boxes'}),
            'qty': forms.TextInput(attrs={'type': 'number', 'class': 'required form-control damage_qty', 'placeholder': 'Enter QTY'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.fields['stock_item'].queryset = SalesStock.objects.filter(qty__gt=0) | SalesStock.objects.filter(pk=instance.stock_item.pk)
        else:
            self.fields['stock_item'].queryset = SalesStock.objects.filter(qty__gt=0)
            
    def clean(self):
        cleaned_data = super().clean()
        stock_item = cleaned_data.get('stock_item')
        input_qty = cleaned_data.get('qty')
        sale_type = cleaned_data.get('sale_type')
        no_boxes = cleaned_data.get('no_boxes')
        
        instance = getattr(self, 'instance', None)
        
        # Check the stock quantity
        if stock_item:
            stock_qty = SalesStock.objects.get(pk=stock_item.pk, is_deleted=False).qty
            if instance and instance.qty:
                if instance.qty != input_qty:
                    available_stock_include_input = stock_qty + instance.qty
                    if not available_stock_include_input >= input_qty:
                        error_message = f"Qty: No stock available in {stock_item.purchase_item.name}, only {stock_qty} left"
                        raise forms.ValidationError(error_message)
            else:
                if stock_qty < input_qty:
                    if stock_qty <= 0:
                        error_message = f"Qty: No stock available in {stock_item.purchase_item.name}"
                    else:
                        error_message = f"Qty: No stock available in {stock_item.purchase_item.name}, only {stock_qty} left"
                    raise forms.ValidationError(error_message)
        
        # Additional validation for no_boxes when sale_type is 'box'
        if sale_type == 'box':
            if no_boxes is None or no_boxes <= 0:
                error_message = "This field is required and must be greater than zero when sale type is 'box'."
                self.add_error('no_boxes', error_message)
        else:
            cleaned_data['no_boxes'] = None  # Ensure no_boxes is not required when sale_type is not 'box'
        
        return cleaned_data