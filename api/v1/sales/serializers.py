from django.conf import settings

from exporting.models import ExportingCountry
from rest_framework import serializers

from main.functions import get_auto_id
from sales_party.models import SalesParty
from sales.models import Sales, SalesExpenses, SalesItems, SalesStock
        
class SalesPartySerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesParty
        fields = ['id','fullname']
    
    def get_fullname(self,obj):
        return obj.get_fullname()
    
class SalesStockSerializer(serializers.ModelSerializer):
    purchase_item = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesStock
        fields = ['id','purchase_item','country']
        
    def get_purchase_item(self,instance):
        return instance.purchase_item.name
    
    def get_country(country_self,instance):
        return instance.country.country_name
        
class ExportingCountrySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ExportingCountry
        fields = ['id','country_name','cash_type']
    
class SalesReportSerializer(serializers.ModelSerializer):
    sales_party = serializers.SerializerMethodField()
    sub_total = serializers.SerializerMethodField()
    sub_total_inr = serializers.SerializerMethodField()
    total_qty = serializers.SerializerMethodField()
    items_total_amount = serializers.SerializerMethodField()
    items_total_inr_amount = serializers.SerializerMethodField()
    items_per_kg_amount = serializers.SerializerMethodField()
    items_total_expence = serializers.SerializerMethodField()
    expenses_items_total_inr_amount = serializers.SerializerMethodField()
    exchange_sub_total = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Sales
        fields = ['id','invoice_no','sales_id','date','sales_party','exchange_rate','country_name','sub_total','sub_total_inr','total_qty','items_total_amount','items_total_inr_amount','items_per_kg_amount','items_total_expence','expenses_items_total_inr_amount','exchange_sub_total']
        
    def get_sales_party(self,obj):
        if obj.sales_party:
           party_name = obj.sales_party.get_fullname()
        else: 
           party_name = ""
        return party_name
    
    def get_sub_total(self,obj):
        return obj.sub_total()
    
    def get_sub_total_inr(self,obj):
        return obj.sub_total_inr()
    
    def get_total_qty(self,obj):
        return obj.total_qty()
    
    def get_items_total_amount(self,obj):
        return obj.items_total_amount()
    
    def get_items_total_inr_amount(self,obj):
        return obj.items_total_inr_amount()
    
    def get_items_per_kg_amount(self,obj):
        return obj.items_per_kg_amount()
    
    def get_items_total_expence(self,obj):
        return obj.items_total_expence()
    
    def get_expenses_items_total_inr_amount(self,obj):
        return obj.expenses_items_total_inr_amount()
    
    def get_exchange_sub_total(self,obj):
        return obj.exchange_sub_total()
    
    def get_country_name(self,obj):
        return obj.country.country_name
    
class SalesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sales
        fields = ['date', 'sales_party']
    
class SalesItemsSerializer(serializers.ModelSerializer):
    sale_type = serializers.SerializerMethodField()
    sales_item = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesItems
        fields = ['sales_item','no_boxes','sale_type','qty','per_kg_amount','amount','amount_in_inr']
        
    def get_sale_type(self,obj):
        return obj.get_sale_type_display()
    
    def get_sales_item(self,obj):
        return obj.sales_stock.purchase_item.name
        
class SalesExpenceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SalesExpenses
        fields = ['title', 'amount','amount_in_inr']