from django.db import models
from django.contrib.auth.models import User

class Food(models.Model):
    FOOD_TYPES = [
        ('Суши', 'Суши'),
        ('Сет', 'Сет'),
        ('Роллы', 'Роллы'),
        ('Сашими', 'Сашими'),
        ('Супы', 'Супы'),
        ('Салаты', 'Салаты'),
        ('Десерты', 'Десерты'),
        ('Напитки', 'Напитки'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название')
    category = models.CharField(max_length=50, choices=FOOD_TYPES, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание')
    image = models.URLField(max_length=200, verbose_name='Ссылка на фото')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    count = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Корзина пользователя {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('cart', 'food')

    def __str__(self):
        return f'{self.food.name} в корзине ({self.quantity} шт.)'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f'Order {self.id}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    food = models.ForeignKey(Food, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.user.username
