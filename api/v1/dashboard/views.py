import requests
import datetime
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Q, Sum, Min, Max
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404

from other_expences.models import OtherExpences
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from main.functions import get_auto_id
from executieves.models import Executive
from purchase_party.models import PurchaseParty
from purchase.models import Purchase, PurchaseExpense, PurchaseItems, PurchaseStock, PurchasedItems
from api.v1.purchase.serializers import PurchaseItemsSerializer, PurchasePartySerializer, PurchaseReportSerializer, PurchaseSerializer
from api.v1.authentication.functions import generate_serializer_errors, get_user_token
from sales.models import Sales, SalesExpenses, SalesItems


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def today_status(request):
    
    purchase = Purchase.objects.filter(date=datetime.today().date(),is_deleted=False)
    todays_purchases = PurchasedItems.objects.filter(purchase__in=purchase,is_deleted=False).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    sales = Sales.objects.filter(date=datetime.today().date(),is_deleted=False)
    todays_sales = SalesItems.objects.filter(sales__in=sales,is_deleted=False).aggregate(total_amount=Sum('amount_in_inr'))['total_amount'] or 0
    
    purchase_expense = PurchaseExpense.objects.filter(purchase__in=purchase,is_deleted=False).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    sales_expense = SalesExpenses.objects.filter(sales__in=sales,is_deleted=False).aggregate(total_amount=Sum('amount_in_inr'))['total_amount'] or 0
    other_expences = OtherExpences.objects.filter(date_added__date=datetime.today().date(),is_deleted=False).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    
    expenses = purchase_expense + sales_expense + other_expences
    
    profit = todays_sales - todays_purchases - purchase_expense - sales_expense - other_expences
    
    groups = request.user.groups.values_list('name', flat=True) 
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": {
            'todays_purchases': todays_purchases,
            'todays_purchase_expenses': purchase_expense,
            'todays_sales': todays_sales,
            'todays_sales_expenses': sales_expense,
            'todays_total_expenses': expenses,
            'profit' : profit,
            'group_names': list(groups),
            },
    }

    return Response(response_data, status_code)