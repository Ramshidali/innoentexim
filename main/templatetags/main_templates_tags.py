from django import template
import re

register = template.Library()

@register.filter(name='format_group_name')
def format_group_name(value):
    return value.replace('_', ' ').title()
