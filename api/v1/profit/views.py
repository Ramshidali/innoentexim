import requests
import datetime
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Q, Sum, Min, Max
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from profit.models import DialyProfit, MonthlyProfit, MyProfit
from api.v1.profit.serializers import DialyProfitSerializer, MonthlyProfitSerializer, MyProfitSerializer

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def dialy_profit(request):
    filter_data = {}
    
    instances = DialyProfit.objects.all().order_by("-date_added")
    
    date_range = request.GET.get('date_range')

    if date_range:
        start_date_str, end_date_str = date_range.split(' - ')
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()
        instances = instances.filter(date_added__range=[start_date, end_date])
        filter_data['date_range'] = date_range
    
    first_date_added = instances.aggregate(first_date_added=Min('date_added'))['first_date_added']
    last_date_added = instances.aggregate(last_date_added=Max('date_added'))['last_date_added']
    
    first_date_formatted = first_date_added.strftime('%m/%d/%Y') if first_date_added else None
    last_date_formatted = last_date_added.strftime('%m/%d/%Y') if last_date_added else None
    
    serialized = DialyProfitSerializer(instances,many=True)
        
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serialized.data,
        "first_date_formatted": first_date_formatted,
        "last_date_formatted": last_date_formatted,
    }

    return Response(response_data, status_code)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def monthly_profit(request):
    filter_data = {}
    
    instances = MonthlyProfit.objects.all().order_by("-date_added")
    
    date_range = request.GET.get('date_range')

    if date_range:
        start_date_str, end_date_str = date_range.split(' - ')
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()
        instances = instances.filter(date_added__range=[start_date, end_date])
        filter_data['date_range'] = date_range
    
    first_date_added = instances.aggregate(first_date_added=Min('date_added'))['first_date_added']
    last_date_added = instances.aggregate(last_date_added=Max('date_added'))['last_date_added']
    
    first_date_formatted = first_date_added.strftime('%m/%d/%Y') if first_date_added else None
    last_date_formatted = last_date_added.strftime('%m/%d/%Y') if last_date_added else None
    
    serialized = MonthlyProfitSerializer(instances,many=True)
        
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serialized.data,
        "first_date_formatted": first_date_formatted,
        "last_date_formatted": last_date_formatted,
    }

    return Response(response_data, status_code)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def my_profit(request):
    filter_data = {}
    
    instances = MyProfit.objects.all()
    
    if request.user.groups.filter(name__in=['core_team','investor']).exists():
        for i in instances:
            print(i.user,"")
            print(request.user)
        instances = instances.filter(user=request.user)
        
    date_range = request.GET.get('date_range')

    if date_range:
        start_date_str, end_date_str = date_range.split(' - ')
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()
        instances = instances.filter(date_added__range=[start_date, end_date])
        filter_data['date_range'] = date_range
        
    first_date_added = MyProfit.objects.aggregate(first_date_added=Min('date_added'))['first_date_added']
    last_date_added = MyProfit.objects.aggregate(last_date_added=Max('date_added'))['last_date_added']
    
    first_date_formatted = first_date_added.strftime('%m/%d/%Y') if first_date_added else None
    last_date_formatted = last_date_added.strftime('%m/%d/%Y') if last_date_added else None
    print(instances)
    serialized = MyProfitSerializer(instances.order_by("-date_added"),many=True)
        
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serialized.data,
        "first_date_formatted": first_date_formatted,
        "last_date_formatted": last_date_formatted,
    }

    return Response(response_data, status_code)