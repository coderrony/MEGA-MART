from django.shortcuts import render, redirect
from cart.models import CartItem
from accounts.models import MyUser
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Products
from django.contrib import messages
import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import random
import string

from django.shortcuts import redirect
from django.urls import reverse

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

# ssl
from sslcommerz_lib import SSLCOMMERZ

# Create your views here.


def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    count_item = cart_items.count()
    if count_item <= 0:
        return redirect("store")
    total = 0
    for item in cart_items:
        total += (item.quantity * item.product.price)

    tax = (total*2) / 100
    grandTotal = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.user = request.user
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]
            order.email = form.cleaned_data["email"]
            order.phone = form.cleaned_data["phone"]
            order.address_line_1 = form.cleaned_data["address_line_1"]
            order.address_line_2 = form.cleaned_data["address_line_2"]
            order.country = form.cleaned_data["country"]
            order.state = form.cleaned_data["state"]
            order.city = form.cleaned_data["city"]
            order.order_note = form.cleaned_data["order_note"]
            order.order_total = grandTotal
            order.tax = tax
            # order.ip = request.META.get["REMOTE_ADDR"]

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                order.ip = x_forwarded_for.split(',')[0]
                print("yes->", order.ip)
            else:
                order.ip = request.META.get('REMOTE_ADDR')  # 127.0.0.1
                print("no->", order.ip)

            order.save()

            y = datetime.datetime.today().strftime("%y")
            m = datetime.datetime.today().strftime("%m")
            d = datetime.datetime.today().strftime("%d")
            order_number = d+m+y+str(d+m+y+str(order.id))
            order.order_number = order_number
            order.save()

            get_order = Order.objects.filter(
                user=request.user, order_number=order_number, is_ordered=False)

            context = {
                'cart_item': cart_items,
                'order': get_order[0],
                'total': total,
                'tax': tax,
                'grandTotal': grandTotal

            }
            return render(request, "orders/payment.html", context)
        else:
            return redirect('checkout')

    else:
        return redirect('checkout')


# def payment(request, order_number):

#     order = Order.objects.get(
#         user=request.user, is_ordered=False, order_number=order_number)

#     # make transaction
#     chars = string.ascii_letters + string.punctuation
#     size = 12
#     transaction = ''.join(random.choice(chars)
#                           for x in range(size)) + str(order_number)

#     payment = Payment.objects.create(user=request.user, transaction=transaction, payment_id=order_number,
#                                      payment_method="Paypal", amount_paid=order.order_total, status=order.status)

#     payment.save()
#     order.payment = payment
#     order.is_ordered = True
#     order.save()

#     # send email to customer
#     customer_email = request.user.email
#     email_subject = 'Payment Confirmation'
#     email_body = render_to_string('orders/payment_confirmation.html', {
#                                   'order': order, 'payment': payment})
#     send_mail(email_subject, email_body, settings.EMAIL_HOST_USER,
#               [customer_email], fail_silently=False)

#     # Cart Item
#     cart_items = CartItem.objects.filter(user=request.user)

#     for item in cart_items:
#         order_product = OrderProduct.objects.create(
#             order=order, payment=payment, user=request.user, product=item.product, quantity=item.quantity, product_price=item.product.price)

#         variation = item.variation.all()
#         order_product.variation.set(variation)
#         order_product.save()

#         product = Products.objects.get(id=item.product.id)
#         product.stock -= item.quantity
#         product.save()
#         item.delete()

#     return redirect(reverse('payment_completed', args=[order_number]))


def payment(request, order_number):

    status_url = request.build_absolute_uri(
        reverse('payment_process', args=[request.user.id]))  # http://127.0.0.1:8000/orders/test/
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=order_number)

    settings = {'store_id': 'ronyd64744b84ef44b',
                'store_pass': 'ronyd64744b84ef44b@ssl', 'issandbox': True}
    sslcommez = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = order.order_total
    post_body['currency'] = "BDT"
    post_body['tran_id'] = order_number
    post_body['success_url'] = status_url
    post_body['fail_url'] = status_url
    post_body['cancel_url'] = "your cancel url"
    post_body['emi_option'] = 0
    post_body['cus_name'] = order.full_name
    post_body['cus_email'] = order.email
    post_body['cus_phone'] = order.phone
    post_body['cus_add1'] = order.address_line_1
    post_body['cus_city'] = order.city
    post_body['cus_country'] = order.country
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = request.user

    response = sslcommez.createSession(post_body)

    return redirect(response["GatewayPageURL"])


@csrf_exempt
def payment_process(request, id):
    user = MyUser.objects.get(id=id)
    # for i, j in request.POST.items():
    #     print(f"{i}--> {j}")

    if request.method == 'POST':
        if request.POST['status'] == 'VALID':

            transaction = request.POST['val_id']
            payment_id = request.POST['tran_id']
            payment_method = request.POST['card_type']
            amount_paid = request.POST['store_amount']
            status = request.POST['status']
            payment = Payment.objects.create(
                user=user, payment_id=payment_id, transaction=transaction,  payment_method=payment_method, amount_paid=amount_paid, status=status)
            payment.save()

            order = Order.objects.get(
                user_id=id, is_ordered=False, order_number=payment_id)
            order.payment = payment
            order.is_ordered = True
            order.save()

            # send email to customer
            customer_email = order.email
            email_subject = 'Payment Confirmation'
            email_body = render_to_string('orders/payment_confirmation.html', {
                'order': order, 'payment': payment})
            send_mail(email_subject, email_body, settings.EMAIL_HOST_USER,
                      [customer_email], fail_silently=False)

            # Cart Item
            cart_items = CartItem.objects.filter(user_id=id)

            for item in cart_items:
                order_product = OrderProduct.objects.create(
                    order=order, payment=payment, user_id=id, product=item.product, quantity=item.quantity, product_price=item.product.price)

                variation = item.variation.all()
                order_product.variation.set(variation)
                order_product.save()

                product = Products.objects.get(id=item.product.id)
                product.stock -= item.quantity
                product.save()
                item.delete()

            return redirect(reverse('payment_completed', args=[payment_id]))

        else:
            messages.error(request, "Request is Fail")
            return redirect("place_order")

    else:
        return redirect("home")


def payment_completed(request, order_number):
    order = Order.objects.filter(
        order_number=order_number, user=request.user).exists()
    print(order)
    if order:
        order = Order.objects.filter(
            order_number=order_number, user=request.user)
        order_product = OrderProduct.objects.filter(
            order=order[0], user=request.user)
        payment = Payment.objects.get(payment_id=order_number)

        context = {
            'order': order[0],
            'payment': payment,
            'order_product': order_product
        }
        return render(request, "orders/complete_order.html", context)

    return redirect("store")
