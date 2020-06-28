from django import template

from fahrtenliste_main import version

register = template.Library()


@register.simple_tag
def programmversion():
    return version.VERSION
