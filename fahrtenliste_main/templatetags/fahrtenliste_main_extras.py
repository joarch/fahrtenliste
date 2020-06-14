from django import template

import version

register = template.Library()


@register.simple_tag
def programmversion():
    return version.VERSION
