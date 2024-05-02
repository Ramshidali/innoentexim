import requests
import datetime
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q, Sum, Min, Max
from django.shortcuts import get_object_or_404

from executieves.models import Executive
from purchase_party.models import PurchaseParty
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from main.functions import get_auto_id
from purchase.models import Purchase, PurchaseExpense, PurchaseItems, PurchaseStock, PurchasedItems
from api.v1.purchase.serializers import PurchaseItemsSerializer, PurchasePartySerializer, PurchaseReportSerializer, PurchaseSerializer
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
    
    instances = Purchase.objects.filter(is_deleted=False)
         
    date_range = request.GET.get('date_range')

    if date_range:
        start_date_str, end_date_str = date_range.split(' - ')
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()
        instances = instances.filter(date__range=[start_date, end_date])
    
    if query:

        instances = instances.filter(
            Q(invoice_no__icontains=query) |
            Q(purchase_id__icontains=query) 
        )
        title = "Purchase Report - %s" % query
        filter_data['q'] = query
        
    first_date_added = instances.aggregate(first_date_added=Min('date'))['first_date_added']
    last_date_added = instances.aggregate(last_date_added=Max('date'))['last_date_added']
    
    first_date_formatted = first_date_added.strftime('%m/%d/%Y') if first_date_added else None
    last_date_formatted = last_date_added.strftime('%m/%d/%Y') if last_date_added else None
    
    serialized = PurchaseReportSerializer(instances,many=True)
        
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
        # if not request.user.is_superuser:
        #     executive = Executive.objects.get(user=request.user,is_deleted=False)
        
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
                    stock.qty += item_data['qty']
                    if not update_purchase_stock.filter(purchase=purchase).exists():
                        stock.purchase.add(purchase)
                    stock.save()
                else:
                    purchase_item = PurchaseItems.objects.get(pk=item_data.purchase_item.pk)
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

            return Response(purchase_serializer.data, status=status.HTTP_201_CREATED)
        return Response(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# def create_purchase(request):
#     if request.method == 'POST':
        
#         auto_id = get_auto_id(Purchase)
#         purchase_id = "IEEIP" + str(auto_id).zfill(3)
        
#         executive = None
#         # if not request.user.is_superuser:
#         #     executive = Executive.objects.get(user=request.user,is_deleted=False)
        
#         data = request.data
#         data['auto_id'] = auto_id
#         data['creator'] = request.user.pk
#         data['executive'] = executive
#         data['purchase_id'] = purchase_id 
        
#         serializer = PurchaseSerializer(data=data)
#         if serializer.is_valid():
#             purchase = serializer.save()

#             # Update stock based on purchased items
#             for item_data in request.data['purchased_items']:
#                 purchase_item_id = item_data['purchase_item']
#                 qty = item_data['qty']

#                 purchase_item = get_object_or_404(PurchaseItems, pk=purchase_item_id)
#                 if (update_purchase_stock:=PurchaseStock.objects.filter(purchase_item=purchase_item,is_deleted=False)).exists():
#                     stock = PurchaseStock.objects.get(purchase_item=purchase_item,is_deleted=False)
#                     stock.qty += qty
#                     if not update_purchase_stock.filter(purchase=purchase).exists():
#                         stock.purchase.add(purchase)
#                     stock.save()
#                 else:
#                     purchase_item = PurchaseItems.objects.get(pk=item_data.purchase_item.pk)
#                     stock_item = PurchaseStock.objects.create(
#                         auto_id = get_auto_id(PurchaseStock),
#                         creator = request.user,
#                         purchase_item = purchase_item,
#                         qty = qty,
#                     )
#                     stock_item.purchase.add(purchase)
#                     stock_item.save()

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)