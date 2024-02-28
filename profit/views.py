import io
import json
import datetime
from datetime import datetime
#django
from django.urls import reverse
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User,Group
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, inlineformset_factory
# rest framework
from rest_framework import status
# local
from main.decorators import role_required
from main.functions import generate_form_errors, get_auto_id, get_current_role, has_group
from . models import *
from . forms import *

# Create your views here.
def calculate_profit(issued_date):
    # Filter purchases for the given date
    purchases = Purchase.objects.filter(date=issued_date, is_deleted=False)
    
    # Calculate total purchase amount
    purchase_total = purchases.aggregate(total=Sum('purchaseditems__amount'))['total'] or 0
    
    # Filter purchase expenses for the given date
    purchase_expenses = PurchaseExpense.objects.filter(purchase__date=issued_date, purchase__is_deleted=False)
    
    # Calculate total purchase expenses amount
    purchase_expense_total = purchase_expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Filter sales for the given date
    sales = Sales.objects.filter(date=issued_date, is_deleted=False)
    
    # Calculate total sales amount
    sales_total = sales.aggregate(total=Sum('salesitems__amount_in_inr'))['total'] or 0
    
    # Filter sales expenses for the given date
    sales_expenses = SalesExpenses.objects.filter(sales__date=issued_date, sales__is_deleted=False)
    
    # Calculate total sales expenses amount
    sales_expense_total = sales_expenses.aggregate(total=Sum('amount_in_inr'))['total'] or 0
    
    # Calculate the profit
    profit = sales_total - purchase_total - purchase_expense_total - sales_expense_total
    
    # Update or create DailyProfit instance
    instance, created = DialyProfit.objects.get_or_create(date_added__date=issued_date)
    instance.purchase = purchase_total
    instance.purchase_expenses = purchase_expense_total
    instance.sales = sales_total
    instance.sales_expenses = sales_expense_total
    instance.total_expenses = purchase_total + sales_expense_total
    instance.profit = profit
    instance.save()
    
    print(profit)
    return profit

@login_required
@role_required(['superadmin','core_team','director'])
def exchange_rates(request):
    """
    Exchange Rate
    :param request:
    :return: Exchange Rate List
    """
    instances = ExchangeRate.objects.filter(is_deleted=False)
    
    context = {
        'instances': instances,
        'page_name' : 'Exchange Rate',
        'page_title' : 'Exchange Rate',
        'is_exchange_rate' : True,
        'is_exchange_rates_page': True,
    }

    return render(request, 'admin_panel/pages/exchange/list.html', context)

@login_required
@role_required(['superadmin','core_team','director'])
def create_exchange_rate(request):
    
    message = ''
    if request.method == 'POST':
        form = ExchangeRateForm(request.POST)
        
        if form.is_valid() :
            data = form.save(commit=False)
            data.auto_id = get_auto_id(ExchangeRate)
            data.creator = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Exchange Rate created successfully.",
                'redirect': 'true',
                "redirect_url": reverse('profit:exchange_rates')
            }
    
        else:
            message = generate_form_errors(form, formset=False)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message,
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        form = ExchangeRateForm()
        
        context = {
            'form': form,
            
            'page_title': 'Create Exchange Rate',
            'url': reverse('profit:create_exchange_rate'),
            'is_exchange_rate' : True,
            'is_exchange_rates_page': True,
        }
        
        return render(request,'admin_panel/pages/exchange/create.html',context)
    
@login_required
@role_required(['superadmin','core_team','director'])
def edit_exchange_rate(request,pk):
    """
    edit operation of export item
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(ExchangeRate, pk=pk)
        
    message = ''
    if request.method == 'POST':
        form = ExchangeRateForm(request.POST,instance=instance)
        
        if form.is_valid():
            
            data = form.save(commit=False)
            data.date_updated = datetime.today()
            data.updater = request.user
            data.save()
                    
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Purchase Item Update successfully.",
                'redirect': 'true',
                "redirect_url": reverse('profit:exchange_rates')
            }
    
        else:
            message = generate_form_errors(form ,formset=False)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        
        form = ExchangeRateForm(instance=instance)

        context = {
            'form': form,
            'page_name' : 'Edit Exchange Rate',
            'page_title' : 'Edit Exchange Rate',
            'url' : reverse('profit:create_exchange_rate'),
            'is_exchange_rate' : True,
            'is_exchange_rates_page': True,  
        }

        return render(request, 'admin_panel/pages/exchange/create.html',context)

@login_required
@role_required(['superadmin','core_team','director'])
def delete_exchange_rate(request, pk):
    """
    exchange rates deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    invoice_numbers_text = ""
    # data = ExchangeRate.objects.get(pk=pk)
    # if not SalesMaterials.objects.filter(export_item=data, is_deleted=False).exists():
        
    #     data.is_deleted=True
    #     data.save()
    
    #     if (instances:=PurchaseMaterials.objects.filter(export_item=data)).exists():
    #         instances.update(is_deleted=True)
            
    #     if (stocks:=Stock.objects.filter(export_item=data)).exists():
    #         stocks.update(is_deleted=True)

    #     response_data = {
    #         "status": "true",
    #         "title": "Successfully Deleted",
    #         "message": "Purchase Item Successfully Deleted.",
    #         "redirect": "true",
    #         "redirect_url": reverse('profit:exchange_rates'),
    #     }
    # else:
    #     sales_material_queryset = SalesMaterials.objects.filter(export_item=data)
    #     sales_invoice_numbers = [sales_material.sales.invoice_no for sales_material in sales_material_queryset]
    #     unique_invoice_numbers = list(set(sales_invoice_numbers))
    #     invoice_numbers_text = ", ".join(unique_invoice_numbers)

    message = f"This export item has already included the sale of some items. Sales Invoice Numbers: {invoice_numbers_text}"
    
    response_data = {
        "status": "false",
        "title": "Failed",
        "message": message,
    }

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
@role_required(['superadmin','core_team','director'])
def profits(request):
    """
    Profits
    :param request:
    :return: Profit List
    """
    instances = DialyProfit.objects.all().order_by("-date_added")
    
    context = {
        'instances': instances,
        'page_name' : 'Profit List',
        'page_title' : 'Profit List',
        'is_profit' : True,
        'is_profit_page': True,
    }

    return render(request, 'admin_panel/pages/profit/list.html', context)