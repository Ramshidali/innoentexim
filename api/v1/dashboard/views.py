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
from sales.models import Sales, SalesExpenses


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def today_status(request):
    
    todays_purchases = Purchase.objects.filter(date=datetime.today().date()).aggregate(total_amount=Sum('purchaseditems__amount'))['total_amount'] or 0
    todays_sales = Sales.objects.filter(date=datetime.today().date()).aggregate(total_amount=Sum('salesitems__amount_in_inr'))['total_amount'] or 0
    
    purchase_expense = PurchaseExpense.objects.filter(purchase__date=datetime.today().date()).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    sales_expense = SalesExpenses.objects.filter(sales__date=datetime.today().date()).aggregate(total_amount=Sum('amount_in_inr'))['total_amount'] or 0
    other_expences = OtherExpences.objects.filter(date_added__date=datetime.today().date()).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    
    expenses = purchase_expense + sales_expense + other_expences
    
    profit = todays_sales - todays_purchases - purchase_expense - sales_expense - other_expences
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": {
            'todays_purchases': todays_purchases,
            'todays_sales': todays_sales,
            'expenses': expenses,
            'profit' : profit,
            },
    }

    return Response(response_data, status_code)