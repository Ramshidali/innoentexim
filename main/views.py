#standerd
import json
import random
import datetime
from datetime import date, timedelta
#django
from django.urls import reverse
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.shortcuts import redirect, render
from django.contrib.auth.models import User,Group
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, HttpResponse
# third party
#local
from main.decorators import role_required
from other_expences.models import OtherExpences
from purchase.models import *
from sales.models import *

# Create your views here.
@login_required
def app(request):
  
    return HttpResponseRedirect(reverse('main:index'))

# Create your views here.
@login_required
# @role_required(['superadmin','core_team','director'])
def index(request):
    purchase = Purchase.objects.filter(date=datetime.today().date(),is_deleted=False)
    todays_purchases = PurchasedItems.objects.filter(purchase__in=purchase,is_deleted=False).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    sales = Sales.objects.filter(date=datetime.today().date(),is_deleted=False)
    todays_sales = SalesItems.objects.filter(sales__in=sales,is_deleted=False).aggregate(total_amount=Sum('amount_in_inr'))['total_amount'] or 0
    
    purchase_expense = PurchaseExpense.objects.filter(purchase__in=purchase,is_deleted=False).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    sales_expense = SalesExpenses.objects.filter(sales__in=sales,is_deleted=False).aggregate(total_amount=Sum('amount_in_inr'))['total_amount'] or 0
    other_expences = OtherExpences.objects.filter(date_added__date=datetime.today().date(),is_deleted=False).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    
    expenses = purchase_expense + sales_expense + other_expences
    
    profit = todays_sales - todays_purchases - purchase_expense - sales_expense - other_expences
    
    context = {
        'todays_purchases': todays_purchases,
        'todays_sales': todays_sales,
        'expenses': expenses,
        'profit' : profit,
        
        'page_name' : 'Dashboard',
        'page_title' : 'Dashboard | Innoentexim',
        'is_dashboard': True,   
    }
  
    return render(request,'admin_panel/index.html', context)