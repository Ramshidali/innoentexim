import calendar

from django import template
from django.db.models import Sum
from django.contrib.auth.models import User,Group

register = template.Library()

@register.simple_tag
def get_month_name(count):
    month_name = calendar.month_name[count]
    return month_name