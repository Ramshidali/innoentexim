import requests
import datetime
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Q, Sum, Min, Max
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404

from profit.views import calculate_profit
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from main.functions import get_auto_id
from executieves.models import Executive
from purchase_party.models import PurchaseParty
from purchase.models import Purchase, PurchaseExpense, PurchaseItems, PurchaseStock, PurchasedItems
from api.v1.purchase.serializers import PurchaseEditSerializer, PurchaseExpenceSerializer, PurchaseItemsSerializer, PurchasePartySerializer, PurchaseReportSerializer, PurchaseSerializer, PurchasedItemsSerializer
from api.v1.authentication.functions import generate_serializer_errors, get_user_token


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def purchase_items(request):
    
    instances = PurchaseItems.objects.filter(is_deleted=False)
    
    serialized = PurchaseItemsSerializer(instances,many=True)
        
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
def purchase_parties(request):
    
    instances = PurchaseParty.objects.filter(is_deleted=False)
    
    serialized = PurchasePartySerializer(instances,many=True)
        
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
def purchase_report(request):
    
    filter_data = {}
    query = request.GET.get("q")
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    if start_date or end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f').date()
    else:
        start_date = datetime.today().date()
        end_date = datetime.today().date()
        
    instances = Purchase.objects.filter(date__gte=start_date,date__lte=end_date,is_deleted=False)
        
    if request.GET.get('partyId'):
        instances = instances.filter(purchase_party__pk=request.GET.get('partyId'))
    
    if query:
        instances = instances.filter(
            Q(invoice_no__icontains=query) |
            Q(purchase_id__icontains=query) 
        )
        title = "Purchase Report - %s" % query
        filter_data['q'] = query
        
    serialized = PurchaseReportSerializer(instances.order_by('-date_added'),many=True)
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
def purchase_info(request,pk):
    
    purchase = Purchase.objects.get(pk=pk)
    
    instances = PurchasedItems.objects.filter(purchase=purchase,is_deleted=False).order_by('-date_added')
    serialized = PurchasedItemsSerializer(instances,many=True)
    
    expences = PurchaseExpense.objects.filter(purchase=purchase,is_deleted=False).order_by('-date_added')
    expence_serialized = PurchaseExpenceSerializer(expences,many=True)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": {
            'purchase_date': purchase.date,
            'purchase_id': purchase.purchase_id,
            'purchase_party': purchase.purchase_party.get_fullname(),
            'purchase_items': {
                'items_data': serialized.data,
                "total_qty": purchase.total_qty(),
                "total_amount_per_kg": purchase.materials_total_amount_per_kg(),
                "total_amount": purchase.materials_total_amount(),
            },
            'purchase_expenses': {
                'expense_data': expence_serialized.data,
                'total_expense': purchase.materials_total_expence(),
            },
            'grand_total': purchase.sub_total(),
        },
    }

    return Response(response_data, status_code)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_purchase(request):
    if request.method == 'POST':
        data = request.data

        # Extract purchase_party primary key from data
        purchase_party_id = data.pop('purchase_party')

        # Extract purchased_items and purchased_expenses data
        purchased_items_data = data.pop('purchased_items', [])
        purchased_expenses_data = data.pop('purchased_expenses', [])

        # Create purchase_party instance
        purchase_party = PurchaseParty.objects.get(pk=purchase_party_id)
        auto_id = get_auto_id(Purchase)
        purchase_id = "IEEIP" + str(auto_id).zfill(3)
        
        executive = None
        if not request.user.is_superuser:
            executive = Executive.objects.get(user=request.user,is_deleted=False)
        try:
            with transaction.atomic():
                # Create Purchase instance
                purchase_serializer = PurchaseSerializer(data=data)
                if purchase_serializer.is_valid():
                    purchase = purchase_serializer.save(
                        purchase_party=purchase_party,
                        auto_id = auto_id,
                        creator = request.user,
                        executive = executive,
                        purchase_id = purchase_id 
                        )

                    # Create PurchasedItems instances
                    for item_data in purchased_items_data:
                        purchase_item_id = item_data.pop('purchase_item')
                        purchase_item = PurchaseItems.objects.get(pk=purchase_item_id)
                        PurchasedItems.objects.create(
                            purchase=purchase, 
                            purchase_item=purchase_item, 
                            auto_id = get_auto_id(PurchasedItems),
                            creator=request.user,
                            **item_data
                            )
                        
                        if (update_purchase_stock:=PurchaseStock.objects.filter(purchase_item=purchase_item,is_deleted=False)).exists():
                            stock = PurchaseStock.objects.get(purchase_item=purchase_item,is_deleted=False)
                            stock.qty += Decimal(item_data['qty'])
                            if not update_purchase_stock.filter(purchase=purchase).exists():
                                stock.purchase.add(purchase)
                            stock.save()
                        else:
                            stock_item = PurchaseStock.objects.create(
                                auto_id = get_auto_id(PurchaseStock),
                                creator = request.user,
                                purchase_item = purchase_item,
                                qty = item_data['qty'],
                            )
                            stock_item.purchase.add(purchase)
                            stock_item.save()

                    # Create PurchaseExpense instances
                    for expense_data in purchased_expenses_data:
                        PurchaseExpense.objects.create(
                            purchase=purchase,
                            auto_id = get_auto_id(PurchaseExpense),
                            creator=request.user,
                            **expense_data)
                        
                    calculate_profit(purchase.date)
                        
                    status_code = status.HTTP_201_CREATED
                    response_data = {
                        "StatusCode": 200,
                        "status": status_code,
                        "data": purchase_serializer.data,
                    }

                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    response_data = {
                        "StatusCode": 400,
                        "status": status_code,
                        "message": purchase_serializer.data,
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
    
    
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_purchase(request,pk):
    if request.method == 'POST':
        data = request.data

        # Extract purchase_party primary key from data
        purchase_party_id = data.pop('purchase_party')

        # Extract purchased_items and purchased_expenses data
        purchased_items_data = data.pop('purchased_items', [])
        purchased_expenses_data = data.pop('purchased_expenses', [])

        # Create purchase_party instance
        purchase_party = PurchaseParty.objects.get(pk=purchase_party_id)
        auto_id = get_auto_id(Purchase)
        purchase_id = "IEEIP" + str(auto_id).zfill(3)
        
        executive = None
        if not request.user.is_superuser:
            executive = Executive.objects.get(user=request.user,is_deleted=False)
        try:
            with transaction.atomic():
                # Create Purchase instance
                purchase_serializer = PurchaseSerializer(data=data)
                if purchase_serializer.is_valid():
                    purchase = purchase_serializer.save(
                        purchase_party=purchase_party,
                        auto_id = auto_id,
                        creator = request.user,
                        executive = executive,
                        purchase_id = purchase_id 
                        )

                    # Create PurchasedItems instances
                    for item_data in purchased_items_data:
                        purchase_item_id = item_data.pop('purchase_item')
                        purchase_item = PurchaseItems.objects.get(pk=purchase_item_id)
                        PurchasedItems.objects.create(
                            purchase=purchase, 
                            purchase_item=purchase_item, 
                            auto_id = get_auto_id(PurchasedItems),
                            creator=request.user,
                            **item_data
                            )
                        
                        if (update_purchase_stock:=PurchaseStock.objects.filter(purchase_item=purchase_item,is_deleted=False)).exists():
                            stock = PurchaseStock.objects.get(purchase_item=purchase_item,is_deleted=False)
                            stock.qty += Decimal(item_data['qty'])
                            if not update_purchase_stock.filter(purchase=purchase).exists():
                                stock.purchase.add(purchase)
                            stock.save()
                        else:
                            stock_item = PurchaseStock.objects.create(
                                auto_id = get_auto_id(PurchaseStock),
                                creator = request.user,
                                purchase_item = purchase_item,
                                qty = item_data['qty'],
                            )
                            stock_item.purchase.add(purchase)
                            stock_item.save()

                    # Create PurchaseExpense instances
                    for expense_data in purchased_expenses_data:
                        PurchaseExpense.objects.create(
                            purchase=purchase,
                            auto_id = get_auto_id(PurchaseExpense),
                            creator=request.user,
                            **expense_data)
                        
                    calculate_profit(purchase.date)
                        
                    status_code = status.HTTP_201_CREATED
                    response_data = {
                        "StatusCode": 200,
                        "status": status_code,
                        "data": purchase_serializer.data,
                    }

                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    response_data = {
                        "StatusCode": 400,
                        "status": status_code,
                        "message": purchase_serializer.data,
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
        purchase = Purchase.objects.get(pk=pk)
        serialized_data = PurchaseEditSerializer(purchase,many=False)
        
        status_code = status.HTTP_201_CREATED
        response_data = {
            "StatusCode": 200,
            "status": status_code,
            "data": serialized_data.data,
        }
            
    return Response(response_data, status=status_code)