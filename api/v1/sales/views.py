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
from api.v1.sales.serializers import ExportingCountrySerializer, SalesExpenceSerializer, SalesItemsSerializer, SalesPartySerializer, SalesReportSerializer, SalesSerializer, SalesStockSerializer
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
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    sales_party = request.GET.get('salesParty')
    country = request.GET.get('country')
    
    if start_date or end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f').date()
    else:
        start_date = datetime.today().date()
        end_date = datetime.today().date()
    
    instances = Sales.objects.filter(date__gte=start_date,date__lte=end_date,is_deleted=False)
    
    if sales_party:
        instances = instances.filter(sales_party__pk=sales_party)
        
    if country:
        instances = instances.filter(country__pk=country)
         
    if query:

        instances = instances.filter(
            Q(invoice_no__icontains=query) |
            Q(sales_id__icontains=query) 
        )
        title = "Sales Report - %s" % query
        filter_data['q'] = query
        
    serialized = SalesReportSerializer(instances.order_by('-date_added'),many=True)
        
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
def sales_info(request,pk):
    
    sales = Sales.objects.get(pk=pk)
    
    instances = SalesItems.objects.filter(sales=sales,is_deleted=False).order_by('-date_added')
    serialized = SalesItemsSerializer(instances,many=True)
    
    expences = SalesExpenses.objects.filter(sales=sales,is_deleted=False).order_by('-date_added')
    expence_serialized = SalesExpenceSerializer(expences,many=True)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": {
            'sales_date': sales.date,
            'sales_id': sales.sales_id,
            'sales_party': sales.sales_party.get_fullname(),
            'sales_country': sales.country.country_name,
            'sales_items': {
                'items_data': serialized.data,
            },
            'sales_expenses': {
                'expense_data': expence_serialized.data,
            },
            "total_qty": sales.total_qty(),
            "total_amount": sales.items_total_amount(),
            "total_amount_inr": sales.items_total_inr_amount(),
            
            "total_amount_expense": sales.items_total_expence(),
            "total_amount_expense_inr": sales.expenses_items_total_inr_amount(),
            
            "total_sub_total_amount": sales.sub_total(),
            "total_sub_total_inr_amount": sales.sub_total_inr(),
        },
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
        
        print(salesd_items_data)
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
                sales_item_id = item_data.pop('sale_item')
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