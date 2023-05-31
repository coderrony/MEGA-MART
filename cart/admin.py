from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'is_available']


admin.site.register(Cart)
