from django import template
from gallery.models import *

register = template.Library()

@register.simple_tag()
def get_categories():
    return Category.objects.all()

@register.inclusion_tag('gallery/nav_bar.html')
def show_categories():
    cats = Category.objects.all()
    return {"cats": cats}