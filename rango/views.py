from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page

def index(request):
	# Query DB for a list of all categories currently stored
	# Order categories by the number of likes in descending order
	# Retrieve top 5 or all if less than 5
	# Place list in the context dictionary which will be passed to the template engine
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]

	context_dict = {}
	context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
	context_dict['categories'] = category_list
	context_dict['pages'] = page_list

	return render(request, 'rango/index.html', context=context_dict)

def about(request):
	return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
	# Context dictionary to be passed to th template rendering engine
	context_dict = {}

	try:
		# If there exists a category name slug with the given name, then return the model instance or raises an exception
		# If not, .get() method raises a DoesNotExist exception
		category = Category.objects.get(slug=category_name_slug)
		
		# Retrieve all associate pages
		# filter() method returns a list of page objects or an empty list
		pages = Page.objects.filter(category=category)

		# Adds the list to the template context under name pages
		context_dict['pages'] = pages

		# Add category object from DB to the context dict
		context_dict['category'] = category
	except Category.DoesNotExist:
		# If the specified category does not exist, then do not do anything and display "no category" message
		context_dict['category'] = None
		context_dict['pages'] = None

	# Render and return the response
	return render(request, 'rango/category.html', context=context_dict)