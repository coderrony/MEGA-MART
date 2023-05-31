
from django.urls import path, include
from . import views


urlpatterns = [
    path("place_order/", views.place_order, name="place_order"),
    path("payment/<order_number>", views.payment, name="payment"),
    path("payment_completed/<order_number>",
         views.payment_completed, name="payment_completed"),
    path("payment_process/<int:id>", views.payment_process, name="payment_process"),

]
