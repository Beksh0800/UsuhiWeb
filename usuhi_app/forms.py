from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Food
from django import forms

class NewsUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')



class AddFoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ('name', 'category','description', 'image', 'price', 'count')
