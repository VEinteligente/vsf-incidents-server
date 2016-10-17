from django import template

register = template.Library()

@register.filter(name='key_value')
def key_value(dic, key):
    return dic[key]
