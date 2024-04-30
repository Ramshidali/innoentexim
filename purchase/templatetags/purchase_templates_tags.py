from django import template
from django.db.models import Sum
from django.contrib.auth.models import User,Group

from purchase.models import Purchase, PurchasedItems, PurchaseExpense
from purchase_party.models import PurchaseParty

register = template.Library()

@register.simple_tag
def get_total_values(queryset):
    instances = queryset.values_list('id', flat=True)
    
    p_items = PurchasedItems.objects.filter(purchase__pk__in=instances)
    items_amount_total = p_items.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    items_qty_total = p_items.aggregate(total_qty=Sum('qty'))['total_qty'] or 0
    
    expences = PurchaseExpense.objects.filter(purchase__pk__in=instances)
    expence_amount_total = expences.aggregate(total_amount_expences=Sum('amount'))['total_amount_expences'] or 0
    
    grand_total = items_amount_total + expence_amount_total
    return{
        'items_amount_total': items_amount_total,
        'items_qty_total': items_qty_total,
        'expences_amount_total': expence_amount_total,
        'grand_total': grand_total,
    }
    
@register.simple_tag
def get_purchase_parties():
    return PurchaseParty.objects.filter(is_deleted=False)