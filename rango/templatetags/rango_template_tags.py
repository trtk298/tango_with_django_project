from django import template
from rango.models import Category

register = template.Library()

@register.inclusion_tag('rango/categories.html')
def get_category_list(curerent_category=None):
	return {'categories': Category.objects.all(),
			'curerent_category': curerent_category}