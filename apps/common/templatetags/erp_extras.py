from django import template

register = template.Library()


@register.filter
def get_attr(obj, field_name):
    """Usage: {{ object|get_attr:field_name }} - resolves choice display names too."""
    display_getter = getattr(obj, f'get_{field_name}_display', None)
    if callable(display_getter):
        try:
            return display_getter()
        except Exception:
            pass
    value = getattr(obj, field_name, '')
    if callable(value):
        try:
            value = value()
        except Exception:
            value = ''
    return value


@register.filter
def verbose_name(obj, field_name):
    try:
        return obj._meta.get_field(field_name).verbose_name.title()
    except Exception:
        return field_name.replace('_', ' ').title()


@register.simple_tag
def url_qs(url_name, *args):
    from django.urls import reverse
    return reverse(url_name, args=args)
