from django import template
from django.db.models import Sum
from django.contrib.auth.models import User,Group
from exporting.models import ExportingCountry

from sales.models import SalesStock

register = template.Library()

@register.simple_tag
def get_sales_countries():
    distinct_countries = SalesStock.objects.values_list('country', flat=True).distinct()
    countries = ExportingCountry.objects.filter(pk__in=distinct_countries)
    # print(countries)
    return countries