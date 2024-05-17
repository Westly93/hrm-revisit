
from django import template

register = template.Library()


@register.filter(name='calculate_total_weight')
def calculate_total_weight(application):
    total_weight = sum(
        [requirement.weight for requirement in application.requirements_met.all()])
    return total_weight


@register.filter(name="is_html")
def is_html(value):
    if '<' in value and '>' in value:
        return True
    return False
