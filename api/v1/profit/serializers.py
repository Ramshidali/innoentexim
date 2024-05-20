import calendar
from django.conf import settings
from rest_framework import serializers
from profit.models import DialyProfit, MonthlyProfit, MyProfit


class DialyProfitSerializer(serializers.ModelSerializer):
    date_added = serializers.DateTimeField(format='%Y-%m-%d')
    
    class Meta:
        model = DialyProfit
        fields = ['id','date_added','purchase','purchase_expenses','sales','sales_expenses','total_expenses','profit']
        
class MonthlyProfitSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    date_added = serializers.DateTimeField(format='%Y-%m-%d')
    
    class Meta:
        model = MonthlyProfit
        fields = ['id','date_added','year','month','total_revenue','other_expences','profit']
    
    def get_month(self,obj):
        month_name = calendar.month_name[obj.month]
        return month_name
        
class MyProfitSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    date_added = serializers.DateTimeField(format='%Y-%m-%d')
    
    class Meta:
        model = MyProfit
        fields = ['id','date_added','year','month','profit']
        
    def get_month(self,obj):
        month_name = calendar.month_name[obj.month]
        return month_name
  