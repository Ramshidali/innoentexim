import random
import requests
import datetime
from decimal import Decimal
from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.db.models import Q, Sum, Min, Max
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError

from profit.views import calculate_profit, profit_calculation
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, renderer_classes

from profit.models import ExchangeRate
from main.functions import get_auto_id
from api.v1.sales.serializers import *
from executieves.models import Executive
from sales_party.models import SalesParty
from exporting.models import ExportingCountry
from sales.models import Sales, SalesExpenses, SalesItems, SalesStock
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
    
    if request.user.groups.filter(name="sales").exists():
        instances = instances.filter(creator=request.user)
    
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

        # Extract sales_items and sales_expenses data
        salesd_items_data = data.pop('sales_items', [])
        salesd_expenses_data = data.pop('sales_expenses', [])
        
        # Create sales_party instance
        sales_party = SalesParty.objects.get(pk=sales_party_id)
        date_part = datetime.today().now().strftime('%Y%m%d')
        random_part = str(random.randint(1000, 9999))
        invoice_number = f'IEEIP-{date_part}-{random_part}'
        auto_id = get_auto_id(Sales)
        sales_id = "IEEIS" + str(auto_id).zfill(3)  
        
        # Create Sales instance
        sales_serializer = SalesSerializer(data=data)
        if sales_serializer.is_valid():
            inr_exchange_rate = ExchangeRate.objects.filter(country=country, is_active=True).latest('-date_added').rate_to_inr
            try:
                with transaction.atomic():
                    sales = sales_serializer.save(
                        auto_id=get_auto_id(Sales),
                        creator=request.user,
                        sales_staff=request.user,
                        sales_id=sales_id,
                        invoice_no=invoice_number,
                        exchange_rate=inr_exchange_rate,
                        country=country,
                        sales_party=sales_party
                    )

                    # Create SalesItems instances
                    for item_data in salesd_items_data:
                        sales_item_id = item_data.pop('sale_item')
                        stock = SalesStock.objects.get(pk=sales_item_id)
                        amount = item_data.get('amount', 0.0)
                                                
                        if item_data['sale_type'].lower() == 'qty': 
                            qty = Decimal(item_data['qty'])
                        elif item_data['sale_type'].lower() == 'box': 
                            qty = Decimal(item_data['no_boxes']) * Decimal(item_data['qty'])

                        # Check if there is enough stock
                        if stock.qty >= Decimal(qty):
                            stock.qty -= Decimal(qty)
                            stock.save()
                        else:
                            raise ValueError(f"Not enough stock for item {sales_item_id}. Available: {stock.qty}, Requested: {qty}")

                        SalesItems.objects.create(
                            auto_id=get_auto_id(SalesItems),
                            creator=request.user,
                            sales=sales, 
                            sales_stock=stock, 
                            amount_in_inr=Decimal(amount) * inr_exchange_rate,
                            **item_data
                        )

                    # Create SalesExpenses instances
                    for expense_data in salesd_expenses_data:
                        amount = expense_data.get('amount', 0.0)
                        SalesExpenses.objects.create(
                            sales=sales,
                            auto_id=get_auto_id(SalesExpenses),
                            creator=request.user,
                            amount_in_inr=Decimal(amount) * inr_exchange_rate,
                            **expense_data
                        )
                    
                    # calculate_profit(sales.date)
                    profit_calculation(sales.date)
                    
                    status_code = status.HTTP_201_CREATED
                    response_data = {
                        "StatusCode": 200,
                        "status": status_code,
                        "message": "Successfully created",
                    }

            except IntegrityError as e:
                status_code = status.HTTP_400_BAD_REQUEST
                response_data = {
                    "StatusCode": 400,
                    "status": "false",
                    "title": "Failed",
                    "message": str(e),
                }

            except Exception as e:
                status_code = status.HTTP_400_BAD_REQUEST
                response_data = {
                    "StatusCode": 400,
                    "status": "false",
                    "title": "Failed",
                    "message": str(e),
                }
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "StatusCode": 400,
                "status": "false",
                "title": "Failed",
                "message": sales_serializer.errors,
            }
            
        return Response(response_data, status=status_code)
        
        
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_sales(request,pk):
    try:
        with transaction.atomic():
            sales_instance = Sales.objects.get(pk=pk)
            sales_items = SalesItems.objects.filter(sales=sales_instance,is_deleted=False)
            sales_expenses = SalesExpenses.objects.filter(sales=sales_instance,is_deleted=False)
            
            for item in sales_items:
                
                if item.sale_type == "box":
                    item_qty = item.qty * item.no_boxes
                else:
                    item_qty = item.qty
                
                stock_instance = SalesStock.objects.filter(purchase_item=item.sales_stock.purchase_item)
                stock_instance = stock_instance.first()
                stock_instance.qty += item_qty
                stock_instance.save()
                
                item.is_deleted = True
                item.save()
            
            sales_expenses.update(is_deleted=True)
            
            sales_instance.is_deleted=True
            sales_instance.save()
            
            # calculate_profit(sales_instance.date)
            profit_calculation(sales_instance.date)
            
            status_code = status.HTTP_200_OK
            response_data = {
                "StatusCode": 200,
                "status": "true",
                "title": "Success",
                "message": "Successfully Deleted",
            }
            
    except IntegrityError as e:
        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            "StatusCode": 400,
            "status": "false",
            "title": "Failed",
            "message": str(e),
        }

    except Exception as e:
        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            "StatusCode": 400,
            "status": "false",
            "title": "Failed",
            "message": str(e),
        }
    
            
    return Response(response_data, status=status_code)