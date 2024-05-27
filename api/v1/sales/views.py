import requests
import random
import datetime
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Q, Sum, Min, Max
from django.shortcuts import get_object_or_404

from exporting.models import ExportingCountry
from profit.models import ExchangeRate
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from main.functions import get_auto_id
from executieves.models import Executive
from sales_party.models import SalesParty
from sales.models import Sales, SalesExpenses, SalesItems, SalesStock
from api.v1.sales.serializers import ExportingCountrySerializer, SalesItemsSerializer, SalesPartySerializer, SalesReportSerializer, SalesSerializer, SalesStockSerializer
from api.v1.authentication.functions import generate_serializer_errors, get_user_token

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def sales_parties(request):
    
    instances = SalesParty.objects.filter(is_deleted=False)
    
    serialized = SalesPartySerializer(instances,many=True)
        
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serialized.data,
    }

    return Response(response_data, status_code)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def export_country(request):
    
    instances = ExportingCountry.objects.filter(is_deleted=False)
    
    serialized = ExportingCountrySerializer(instances,many=True)
        
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serialized.data,
    }

    return Response(response_data, status_code)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def sales_stock(request):
    
    instances = SalesStock.objects.filter(is_deleted=False)
    if request.GET.get("country_id"):
        instances = instances.filter(country__pk=request.GET.get("country_id"))
        
    serialized = SalesStockSerializer(instances,many=True)
        
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serialized.data,
    }

    return Response(response_data, status_code)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def sales_report(request):
    
    filter_data = {}
    query = request.GET.get("q")
    
    instances = Sales.objects.filter(is_deleted=False)
         
    date_range = request.GET.get('date_range')

    if date_range:
        start_date_str, end_date_str = date_range.split(' - ')
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()
        instances = instances.filter(date__range=[start_date, end_date])
    
    if query:

        instances = instances.filter(
            Q(invoice_no__icontains=query) |
            Q(sales_id__icontains=query) 
        )
        title = "Sales Report - %s" % query
        filter_data['q'] = query
        
    first_date_added = instances.aggregate(first_date_added=Min('date'))['first_date_added']
    last_date_added = instances.aggregate(last_date_added=Max('date'))['last_date_added']
    
    first_date_formatted = first_date_added.strftime('%m/%d/%Y') if first_date_added else None
    last_date_formatted = last_date_added.strftime('%m/%d/%Y') if last_date_added else None
    
    serialized = SalesReportSerializer(instances.order_by('-date_added'),many=True)
        
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serialized.data,
        "first_date_formatted": first_date_formatted,
        "last_date_formatted": last_date_formatted,
    }

    return Response(response_data, status_code)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_sales(request):
    if request.method == 'POST':
        data = request.data

        # Extract sales_party primary key from data
        sales_party_id = data.pop('sales_party')
        country = ExportingCountry.objects.get(pk=data.pop('country'))

        # Extract salesd_items and salesd_expenses data
        salesd_items_data = data.pop('sales_items', [])
        salesd_expenses_data = data.pop('sales_expenses', [])

        # Create sales_party instance
        sales_party = SalesParty.objects.get(pk=sales_party_id)
        date_part = datetime.now().strftime('%Y%m%d')
        random_part = str(random.randint(1000, 9999))
        invoice_number = f'IEEIP-{date_part}-{random_part}'
        auto_id = get_auto_id(Sales)
        sales_id = "IEEIS" + str(auto_id).zfill(3)  
        
        # Create Sales instance
        sales_serializer = SalesSerializer(data=data)
        if sales_serializer.is_valid():
            inr_exchange_rate = ExchangeRate.objects.filter(country=country,is_active=True).latest('-date_added').rate_to_inr
            
            sales = sales_serializer.save(
                auto_id = get_auto_id(Sales),
                creator = request.user,
                sales_staff = request.user,
                sales_id = sales_id,
                invoice_no = invoice_number,
                exchange_rate = inr_exchange_rate,
                country = country,
                sales_party = sales_party
                )

            # Create SalesItems instances
            for item_data in salesd_items_data:
                sales_item_id = item_data.pop('sales_item')
                stock = SalesStock.objects.get(pk=sales_item_id)
                amount = item_data.get('amount', 0.0)
                
                sales_item_instance = SalesItems.objects.create(
                    auto_id = get_auto_id(SalesItems),
                    creator=request.user,
                    sales=sales, 
                    sales_stock=stock, 
                    amount_in_inr=Decimal(amount) * inr_exchange_rate,
                    **item_data
                    )
                
                if stock.qty >= Decimal(item_data['qty']) :
                    stock.qty -= Decimal(item_data['qty'])
                    stock.save()
                else: 
                    response_data = {
                        "StatusCode": 6001,
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "no stock available",
                    }

                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            # Create SalesExpenses instances
            for expense_data in salesd_expenses_data:
                amount = expense_data.get('amount', 0.0)
                SalesExpenses.objects.create(
                    sales=sales,
                    auto_id = get_auto_id(SalesExpenses),
                    creator=request.user,
                    amount_in_inr=Decimal(amount) * inr_exchange_rate,
                    **expense_data)

            return Response(sales_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(sales_serializer.errors, status=status.HTTP_400_BAD_REQUEST)