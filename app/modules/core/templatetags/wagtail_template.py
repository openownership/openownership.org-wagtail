# 3rd party
import arrow
from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def sort_link(context, value):
    sort_field = context.get('sort_field')
    sort_order = context.get('sort_order')
    query_dict = context.request.GET.copy()

    if value == sort_field:
        sort_order = 'asc' if sort_order == 'desc' else 'desc'

    query_dict['sort_field'] = value
    query_dict['sort_order'] = sort_order

    return f'?{query_dict.urlencode()}'


@register.filter
def shift_days(value, days):
    return arrow.get(value).shift(days=days).format('YYYY-MM-DD')


@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__
