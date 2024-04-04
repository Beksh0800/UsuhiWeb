from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import Food, Cart, CartItem, Profile
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import logging
logger = logging.getLogger(__name__)

# Внутри вашего view



def food_page(request):
    foods = Food.objects.all()

    # Получаем корзину текущего пользователя, если он аутентифицирован
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
    else:
        cart_items = []

    FOOD_TYPES = Food.FOOD_TYPES
    context = {'foods': foods, 'FOOD_TYPES': FOOD_TYPES, 'cart_items': cart_items}
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

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    return render(request, 'cart.html', {'cart_items': cart_items})


@login_required
def view_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Если профиль не существует, создаем новый профиль для текущего пользователя
        profile = Profile.objects.create(user=request.user)  # Предполагается, что Profile имеет поле user

    context = {
        'profile': profile
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

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
    FOOD_TYPES = Food.FOOD_TYPES
    context = {'foods': foods, 'FOOD_TYPES': FOOD_TYPES}
    return render(request, 'all_foods.html', context)


@login_required
@require_POST
def modify_cart(request):
    try:
        action = request.POST.get('action')
        food_id = request.POST.get('food_id')
        quantity = int(request.POST.get('quantity', 0))

        food = get_object_or_404(Food, id=food_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, food=food)

        # Если cart_item только что создан, установите quantity в 0
        if created:
            cart_item.quantity = 0

        if action == 'add':
            cart_item.quantity += quantity
        elif action == 'remove':
            cart_item.quantity -= quantity
            if cart_item.quantity <= 0:
                cart_item.delete()
                return JsonResponse({'success': True, 'quantity': 0})

        # Убедитесь, что cart_item еще существует перед сохранением
        if cart_item.id:
            cart_item.save()
            return JsonResponse({'success': True, 'quantity': cart_item.quantity})
        else:
            return JsonResponse({'success': True, 'quantity': 0})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


from django.shortcuts import get_object_or_404

@require_POST
def remove_from_cart(request):
    user = request.user
    food_id = request.POST.get('food_id')
    if not food_id:
        return JsonResponse({'error': 'Missing food_id'}, status=400)

    try:
        # Получаем объект корзины текущего пользователя
        cart = get_object_or_404(Cart, user=user)
        # Прямое удаление товара из корзины
        CartItem.objects.filter(cart=cart, food_id=food_id).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def remove_from_cart_view(request):
    if request.method == 'POST':
        food_id = request.POST.get('food_id')
        try:
            item = CartItem.objects.get(food_id=food_id, cart__user=request.user)
            item.delete()
            return JsonResponse({'success': True})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден в корзине'})


