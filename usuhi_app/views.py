from django.shortcuts import render, get_object_or_404, redirect
from .models import Food
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

def food_page(request):
    food = Food.objects.all()
    context = {
        'food': food,
    }
    return render(request, "./foods_page.html", context)


def about_page(request):
    return render(request, 'about_page.html')

def signup_page(request):
    if request.method == 'POST':
        form = NewsUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login_page")
    else:
        form = NewsUserForm()

    context = {'form': form}
    return render(request, './signup.html', context)

def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("food_page")

    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, './login.html', context)

def logout_request(request):
    logout(request)
    return redirect("food_page")

def add_food_page(request):
    if request.method == 'POST':
        form = AddFoodForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_food_page')
    else:
        form = AddFoodForm()

    context = {'form': form}
    return render(request, './add_food_page.html', context)

def food_detail_page(request, pk):
    food = get_object_or_404(Food, pk=pk)
    context = {
        'food': food,
    }
    return render(request, './food_detail_page.html', context)

def edit_food_page(request, pk):
    food = get_object_or_404(Food, pk=pk)
    form = AddFoodForm(request.POST or None, request.FILES or None, instance=food)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('food_detail_page', pk=food.pk)

    context = {
        'food': food,
        'form': form
    }

    return render(request, './edit_food_page.html', context)

def delete_food_page(request, pk):
    food = get_object_or_404(Food, pk=pk)
    if request.method == 'POST':
        food.delete()
        return redirect('all_food_page')

    context = {
        'food': food
    }

    return render(request, './delete_food_page.html', context)

def all_food_page(request):
    foods = Food.objects.all()
    context = {'foods': foods}
    return render(request, './all_foods.html', context)
