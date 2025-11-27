from django import template

register = template.Library()

@register.filter
def replace_underscore(value):
    """Replace underscores with spaces"""
    return value.replace('_', ' ')
