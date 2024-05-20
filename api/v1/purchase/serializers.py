from django.conf import settings

from main.functions import get_auto_id
from purchase_party.models import PurchaseParty
from rest_framework import serializers

from purchase.models import Purchase, PurchaseExpense, PurchaseItems, PurchasedItems

class PurchaseItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItems
        fields = ['id','name']
        
class PurchasePartySerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseParty
        fields = ['id','fullname']
    
    def get_fullname(self,obj):
        return obj.get_fullname()

class PurchaseReportSerializer(serializers.ModelSerializer):
    purchase_party_name = serializers.SerializerMethodField()
    total_qty = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    total_expense = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Purchase
        fields = ['id','purchase_id','date','purchase_party_name','total_qty','total_amount','total_expense','grand_total']
        
    def get_purchase_party_name(self,obj):
        return obj.purchase_party.get_fullname()
    
    def get_total_qty(self,obj):
        return obj.total_qty()
    
    def get_total_amount(self,obj):
        return obj.materials_total_amount()
    
    def get_total_expense(self,obj):
        return obj.materials_total_expence()
    
    def get_grand_total(self,obj):
        return obj.sub_total()
    
class PurchasedItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PurchasedItems
        fields = ['qty', 'amount', 'purchase_item']
        
class PurchaseExpenceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PurchaseExpense
        fields = ['title', 'amount']

class PurchaseSerializer(serializers.ModelSerializer):
    purchase_party = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = ['id','purchase_id', 'date', 'purchase_party', 'executive']
        read_only_fields = ['purchase_id', 'purchase_party', 'executive']
        
    def get_purchase_party(self,obj):
        return obj.purchase_party.get_fullname()