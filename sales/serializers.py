from rest_framework import serializers
from sales.models import SalesStock


# **********************************************************************************************
                                                # GET Method
# **********************************************************************************************
class SalesStockSerializer(serializers.ModelSerializer):
    purchase_item = serializers.SerializerMethodField()

    class Meta:
        model = SalesStock
        fields = ['id','purchase_item']
        
    def get_purchase_item(self,instance):
        return instance.purchase_item.name