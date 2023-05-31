from django.db import models
from store.models import Products, Variation
from accounts.models import MyUser
# Create your models here.


class Cart(models.Model):
    cart_id = models.CharField(max_length=200)
    cart_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    variation = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_available = models.BooleanField(default=True)

    def get_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name
