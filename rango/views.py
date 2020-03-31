from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

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

@login_required
def add_category(request):
	form = CategoryForm()
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)
			return redirect('/rango')
		else:
			print(form.errors)
	return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except:
		category = None

	if category is None:
		return redirect(reverse('rango:index'))

	form = PageForm()

	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()

				return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
		else:
			print(form.errors)

	context_dict ={'form': form, 'category': category}
	return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
	registered = False

	if request.method == 'POST':
		user_form = UserForm(request.POST)
		profile_form = UserProfileForm(request.POST)

		if user_form.is_valid() and profile_form.is_valid:
			user = user_form.save()
			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()

			registered = True
		else:
			print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, 'rango/register.html', context = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return redirect(reverse('rango:index'))
			else:
				return HttpResponse("Your Rango account is disabled.")

		else:
			print(f"Invalid login details: {username}, {password}")
			return HttpResponse("Invalid login details supplied.")

	else:
		return render(request, 'rango/login.html')

@login_required
def restricted(request):
	return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
	logout(request)
	return redirect(reverse('rango:index'))