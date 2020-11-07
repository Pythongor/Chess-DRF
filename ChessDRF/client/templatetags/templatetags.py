from django.template import Library
# from django.template.defaultfilters import stringfilter

register = Library()


@register.filter(name='get')
def get(dictionary, key):
    return dictionary.get(key)


@register.filter(name='concat')
def concat(first, second):
    return f'{first}{second}'
