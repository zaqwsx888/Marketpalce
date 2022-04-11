from django import template
from urllib.parse import urlencode
register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Фильтр для получения значения по ключу из словаря в шаблоне."""
    return dictionary.get(key)


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    query.pop('page', None)
    query.update(kwargs)
    return query.urlencode()
