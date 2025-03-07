from django import template

register = template.Library()


@register.filter
def get_fields(obj):
    return [{'name': f.name, 'value': getattr(obj, f.name)} for f in obj._meta.fields]
