from django.contrib import admin
from .models import Payment, Order, OrderProduct
# Register your models here.

admin.site.register(Payment)
admin.site.register(OrderProduct)


class orderProductAdmin(admin.TabularInline):
    model = OrderProduct
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'order_number', 'email', 'phone']

    search_fields = ['order_number', 'email']

    inlines = [orderProductAdmin]
