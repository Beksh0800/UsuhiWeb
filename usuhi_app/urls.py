from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.food_page, name='food_page'),
    path('user/signup/', views.signup_page, name='signup_page'),
    path('user/login/', views.login_page, name='login_page'),
    path('about/', views.about_page, name='about_page'),
    path('user/logout/', views.logout_request, name='logout_request'),
    path('food/add/', views.add_food_page, name='add_food_page'),
    path('food/detail/<int:pk>/', views.food_detail_page, name='food_detail_page'),
    path('food/delete/<int:pk>/', views.delete_food_page, name='delete_food_page'),
    path('food/edit/<int:pk>/', views.edit_food_page, name='edit_food_page'),
    path('food/all/', views.all_food_page, name='all_food_page'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('cart/', views.view_cart, name='cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('modify_cart/', views.modify_cart, name='modify_cart'),
    path('save_order/', views.save_order, name='save_order'),
    path('order/create/', views.order_create, name='order_create'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('profile/change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
]
