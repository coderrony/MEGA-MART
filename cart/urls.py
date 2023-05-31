from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('<int:product_id>', views.add_cart, name='add_cart'),
    path('decrease/<int:productId>/<int:cart_id>',
         views.decrease_item, name='decrease'),
    path('removeCart/<int:product_id>/<int:cart_id>',
         views.remove_cart, name='removeCart'),
    path('checkout/',
         views.checkout, name='checkout'),
]
