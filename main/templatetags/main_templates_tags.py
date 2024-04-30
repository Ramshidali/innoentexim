from django import template
from django.contrib.auth.models import User,Group
import re

from exporting.models import EXPORT_STATUS, CourierPartner, ExportingCountry
from investors.models import Investors
from other_expences.models import ExpenceTypes
from sales_party.models import SalesParty

register = template.Library()

@register.filter(name='format_group_name')
def format_group_name(value):
    return value.replace('_', ' ').title()

@register.simple_tag
def get_have_group(user_id, group_name):
    status = False
    try:
        user = User.objects.get(pk=user_id)
        if user.is_superuser or user.groups.filter(name=group_name).exists():
            status = True
    except User.DoesNotExist:
        pass
    return status

@register.simple_tag
def get_countries():
    return ExportingCountry.objects.filter(is_deleted=False)

@register.simple_tag
def get_courier_partners():
    return CourierPartner.objects.filter(is_deleted=False)

@register.simple_tag
def get_courier_status():
    return EXPORT_STATUS

@register.simple_tag
def get_sales_parties():
    return SalesParty.objects.filter(is_deleted=False)

@register.simple_tag
def get_expence_types():
    return ExpenceTypes.objects.filter(is_deleted=False)

@register.simple_tag
def get_investors():
    return Investors.objects.filter(is_deleted=False)