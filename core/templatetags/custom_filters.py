
# templatetags/custom_filters.py
# from django import template
# register = template.Library()

# @register.filter
# def get(dict_data, key):
#     return dict_data.get(key)

# templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def dict_get(d, key):
    return d.get(key) if isinstance(d, dict) else None

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0
