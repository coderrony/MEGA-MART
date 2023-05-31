from django.urls import path
from . import views
urlpatterns = [
    path('', views.store, name='store'),
    path('<slug:product_item>', views.store, name='product_item'),
    path('<slug:product_item>/<slug:single_item>',
         views.single_proudcts_item, name='single_item'),
    path('search/', views.search, name='search'),
    path('review_submit/<int:product_id>/', views.review, name='review'),
]
