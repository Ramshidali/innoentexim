from django import template
from django.contrib.auth.models import User,Group
import re

register = template.Library()

@register.filter(name='format_group_name')
def format_group_name(value):
    return value.replace('_', ' ').title()

@register.simple_tag
def get_have_group(user_id, group_name):
    status = False
    try:
        user = User.objects.get(pk=user_id)
        if user.groups.filter(name=group_name).exists():
            status = True
    except User.DoesNotExist:
        pass
    return status