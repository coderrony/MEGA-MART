from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logoutView, name="logout"),
    path('activation/<uidb64>/<token>',
         views.activation, name="activation"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('forgetPassword/', views.forgetPassword, name="forgetPassword"),
    path('changePassword/<uidb64>/<token>',
         views.changePassword, name="changePassword"),
    path('savePassword/', views.savePassword, name="savePassword"),
    path('my_orders/', views.my_orders, name="my_orders"),
    path('order_details/<int:order_id>/',
         views.order_details, name="order_details"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('change_password/', views.change_password, name="change_password"),

]
