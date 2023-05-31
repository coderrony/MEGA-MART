from django.shortcuts import render
from store.models import Products
# Create your views here.


def home(request):
    products = Products.objects.filter(is_available=True)
    return render(request, 'home.html', context={'products': products})
