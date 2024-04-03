from django.db import models


class Food(models.Model):
    # 'name', 'description', 'image', 'price', 'count'
    name = models.CharField("Название", max_length=100)
    category = models.CharField("Category", max_length=100)
    description = models.TextField("Description")
    image = models.CharField("Ссылка на фото", max_length=200)
    price = models.IntegerField("Price")
    count = models.IntegerField("Количество")

    def __str__(self):
        return self.name


