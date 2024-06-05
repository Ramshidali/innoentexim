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
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    if start_date or end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f').date()
    else:
        start_date = datetime.today().date()
        end_date = datetime.today().date()
    
    instances = DialyProfit.objects.filter(date_added__gte=start_date,date_added__lte=end_date).order_by("-date_added")
    serialized = DialyProfitSerializer(instances,many=True)
        
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
def monthly_profit(request):
    filter_data = {}
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    if start_date or end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f').date()
    else:
        start_date = datetime.today().date()
        end_date = datetime.today().date()
    
    instances = MonthlyProfit.objects.filter(date_added__gte=start_date,date_added__lte=end_date).order_by("-date_added")
    serialized = MonthlyProfitSerializer(instances,many=True)
        
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
def my_profit(request):
    filter_data = {}
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    if start_date or end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f').date()
    else:
        start_date = datetime.today().date()
        end_date = datetime.today().date()
    
    instances = MyProfit.objects.filter(date_added__gte=start_date,date_added__lte=end_date)
    if request.user.groups.filter(name='investor').exists():
        instances = instances.filter(user=request.user)
    serialized = MyProfitSerializer(instances.order_by("-date_added"),many=True)
        
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serialized.data,
    }

    return Response(response_data, status_code)