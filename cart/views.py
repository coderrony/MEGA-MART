from django.shortcuts import render, redirect, get_object_or_404
from store.models import Products, Variation
from .models import Cart, CartItem
from orders.models import Order
from .forms import OrderForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import uuid
# Create your views here.


def _get_session(request):
    session_key = request.session.get('session_key', None)
    if not session_key:
        session_key = str(uuid.uuid4())
        request.session['session_key'] = session_key
    return session_key
# def _get_session(request):
#     sessionKey = request.session.session_key
#     if not sessionKey:
#         sessionKey = request.session.create()
#     return sessionKey


def add_cart(request, product_id):
    product = Products.objects.get(id=product_id)
    if request.user.is_authenticated:
        product_variation = []
        cartId = None
        if request.method == 'POST':
            for i in request.POST:
                key = i
                value = request.POST[i]

                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    print(variation)
                except:
                    pass

        print(product_variation)
        print(request.user)
        is_cartItem_exist = CartItem.objects.filter(
            product=product, user=request.user).exists()

        print(is_cartItem_exist)

        if is_cartItem_exist:
            cart_item = CartItem.objects.filter(
                product=product, user=request.user)
            ex_variation_list = []
            ex_variation_id = []
            for item in cart_item:
                ex_variation = item.variation.all()
                ex_variation_list.append(list(ex_variation))
                ex_variation_id.append(item.id)

            print(ex_variation_list, ex_variation_id)

            if product_variation in ex_variation_list:
                index = ex_variation_list.index(product_variation)
                id = ex_variation_id[index]
                get_item = CartItem.objects.get(
                    product=product, id=id)
                get_item.quantity += 1
                get_item.save()
            else:
                cart_item = CartItem.objects.create(
                    product=product, user=request.user, quantity=1)
                if product_variation is not None:
                    cart_item.variation.add(*product_variation)
                cart_item.save()

        else:
            print("yes")
            cart_item = CartItem.objects.create(
                product=product, user=request.user, quantity=1)
            if product_variation is not None:
                cart_item.variation.add(*product_variation)
            cart_item.save()

    else:
        product_variation = []
        cartId = None
        if request.method == 'POST':

            for i in request.POST:
                key = i
                value = request.POST[i]

                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    print(variation)
                except:
                    pass

        try:
            cartId = Cart.objects.get(cart_id=_get_session(request))
        except:
            cartId = Cart.objects.create(cart_id=_get_session(request))
            cartId.save()

        is_cartItem_exist = CartItem.objects.filter(
            product=product, cart=cartId).exists()

        if is_cartItem_exist:
            cart_item = CartItem.objects.filter(product=product, cart=cartId)
            ex_variation_list = []
            ex_variation_id = []
            for item in cart_item:
                ex_variation = item.variation.all()
                ex_variation_list.append(list(ex_variation))
                ex_variation_id.append(item.id)

            print(ex_variation_list, ex_variation_id)

            if product_variation in ex_variation_list:
                index = ex_variation_list.index(product_variation)
                id = ex_variation_id[index]
                get_item = CartItem.objects.get(
                    product=product, cart=cartId, id=id)
                get_item.quantity += 1
                get_item.save()
            else:
                cart_item = CartItem.objects.create(
                    product=product, cart=cartId, quantity=1)
                if product_variation is not None:
                    cart_item.variation.add(*product_variation)
                cart_item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product, cart=cartId, quantity=1)
            if product_variation is not None:
                cart_item.variation.add(*product_variation)
            cart_item.save()

    return redirect('cart')


def decrease_item(request, productId, cart_id):
    product = get_object_or_404(Products, id=productId)
    # product = Products.objects.get(id=productId)
    if request.user.is_authenticated:
        cartItem = CartItem.objects.get(
            product=product, user=request.user, id=cart_id)
    else:
        cart = Cart.objects.get(cart_id=_get_session(request))
        cartItem = CartItem.objects.get(product=product, cart=cart, id=cart_id)

    if cartItem.quantity > 1:
        cartItem.quantity -= 1
        cartItem.save()
    else:
        cartItem.delete()

    return redirect('cart')


def remove_cart(request, product_id, cart_id):
    product = Products.objects.get(id=product_id)
    cart_item = CartItem.objects.get(product=product, id=cart_id)
    cart_item.delete()
    return redirect('cart')


def cart(request):
    total = 0
    tax = None
    cart_item = None
    grandTotal = None

    try:

        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_get_session(request))
            cart_item = CartItem.objects.filter(cart=cart,
                                                is_available=True)

        for item in cart_item:
            total += (item.product.price * item.quantity)

        tax = (total * 2) / 100
        grandTotal = tax + total

    except:
        pass

    return render(request, 'cart/cart.html', context={"total": total, 'tax': tax, 'grandTotal': grandTotal, 'cart_item': cart_item})


@login_required(login_url="login")
def checkout(request):

    cart_item = None

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(user=request.user,
                                                is_available=True)

    except:
        pass

    is_ordered = Order.objects.filter(
        user=request.user, is_ordered=True).exists()
    if is_ordered:
        form = OrderForm(instance=Order.objects.filter(
            user=request.user, is_ordered=True).order_by("-create_at")[0])
    else:
        form = OrderForm()

    return render(request, 'cart/checkout.html', context={'cart_item': cart_item, "form": form})
