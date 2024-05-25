from django.shortcuts import render, get_object_or_404, redirect
from .models import Food, Cart, CartItem, Profile,  Order, OrderItem
from .forms import ProfileForm, UserUpdateForm, OrderCreateForm, CustomPasswordChangeForm, AddFoodForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Food, Cart, CartItem, Profile
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

def food_page(request):
    foods = Food.objects.all()
    cart_items = {}

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = {item.food.id: item.quantity for item in cart.items.all()}

    FOOD_TYPES = Food.FOOD_TYPES
    context = {
        'foods': foods,
        'FOOD_TYPES': FOOD_TYPES,
        'cart_items': cart_items
    }
    return render(request, "foods_page.html", context)

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
    foods = Food.objects.all()
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = {item.food.id: item.quantity for item in cart.items.all()}

    FOOD_TYPES = Food.FOOD_TYPES
    context = {
        'foods': foods,
        'FOOD_TYPES': FOOD_TYPES,
        'cart_items': cart_items
    }
    return render(request, "cart.html", context)



@login_required
def view_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('view_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'profile.html', context)

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('view_profile')
    template_name = 'change_password.html'

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)

@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('view_profile')

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('view_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
        password_form = CustomPasswordChangeForm(user=request.user)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'edit_profile.html', context)

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

        if created:
            cart_item.quantity = 0

        if action == 'add':
            cart_item.quantity += quantity
        elif action == 'remove':
            cart_item.quantity -= quantity
            if cart_item.quantity <= 0:
                cart_item.delete()
                return JsonResponse({'success': True, 'quantity': 0})

        if cart_item.id:
            cart_item.save()
            return JsonResponse({'success': True, 'quantity': cart_item.quantity})
        else:
            return JsonResponse({'success': True, 'quantity': 0})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def remove_from_cart(request):
    user = request.user
    food_id = request.POST.get('food_id')
    if not food_id:
        return JsonResponse({'error': 'Missing food_id'}, status=400)

    try:
        cart = get_object_or_404(Cart, user=user)
        CartItem.objects.filter(cart=cart, food_id=food_id).delete()

        cart_items_count = cart.items.count()

        return JsonResponse({'success': True, 'cart_items_count': cart_items_count})
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

@csrf_exempt
def save_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/')
        db = client.Usuhi2
        collection = db.orders
        collection.insert_one(data)
        return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def order_create(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.food, price=item.food.price, quantity=item.quantity)
            cart_items.delete()
            return redirect('order_success', order_id=order.id)
    else:
        form = OrderCreateForm()
    return render(request, 'shop/order_create.html', {'cart_items': cart_items, 'form': form})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_success.html', {'order': order})
