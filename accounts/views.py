from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

from django.contrib import messages
from .models import MyUser, UserProfile
from django.http import HttpResponse
from cart.models import CartItem, Cart
from cart.views import _get_session
from orders.models import Order, OrderProduct
from django.contrib.auth.hashers import check_password
# verification
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model

# Create your views here.


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = make_password(form.cleaned_data['password'])
            username = email.split("@")[0]
            print(username)
            print(password)
            user = MyUser.objects.create(first_name=first_name, last_name=last_name,
                                         email=email, password=password, username=username)
            user.phone = phone
            user.save()

            # Generate verification code
            verification_code = default_token_generator.make_token(user)

            # Send email with verification link
            subject = 'Verify your email'
            current_site = get_current_site(request)
            message = render_to_string('accounts/verification_email.html', {
                'user': user,
                'domain': current_site,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'verification_code': verification_code,
            })
            print('uid', user.id, verification_code)

            to_email = email
            send_mail = EmailMessage(subject, message, to=[to_email])
            send_mail.send()

            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", context={'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        # print(email, password)

        if user is not None:
            try:

                cart = Cart.objects.get(cart_id=_get_session(request))
                is_cart_exits = CartItem.objects.filter(cart=cart).exists()
                if is_cart_exits:
                    cartItem = CartItem.objects.filter(cart=cart)
                    product_variation = []

                    for item in cartItem:
                        p = item.variation.all()
                        product_variation.append((list(p), item.quantity))

                    print(product_variation)

                    ex_variation = []
                    ex_id = []
                    cartItem = CartItem.objects.filter(user=user)

                    for item in cartItem:
                        ex_variation.append(list(item.variation.all()))
                        ex_id.append(item.id)

                    print(cartItem)

                    for pr in product_variation:
                        if pr[0] in ex_variation:
                            index = ex_variation.index(pr[0])
                            item_id = ex_id[index]
                            get_item = CartItem.objects.get(id=item_id)
                            get_item.quantity += pr[1]
                            get_item.user = user
                            get_item.save()
                        else:
                            cartItem = CartItem.objects.filter(cart=cart)
                            for item in cartItem:
                                print(item, "<-")
                                item.user = user
                                item.save()
            except:
                pass

            login(request, user)
            messages.success(request, "Successfully Login"
                             )
            cart_item_count = CartItem.objects.filter(
                user=request.user).count()
            if cart_item_count > 0:
                return redirect("checkout")
            else:
                return redirect("dashboard")
        else:
            messages.error(request, "invalid login")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logoutView(request):
    logout(request)
    messages.success(request, 'you are logout')
    return redirect("login")


# def activation(request, uidb64, token):
#     return HttpResponse("ok")

def activation(request, uidb64, token):
    print("activation is here ", uidb64, token)

    try:
        # user account id like 20,31
        uid = urlsafe_base64_decode(uidb64).decode()
        user = MyUser.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Activate user account
        user.is_active = True
        user.save()

        # Redirect to login page
        return redirect('login')

    # If activation fails, redirect to an error page or show an error message
    return redirect('activation_failed')


@login_required(login_url="login")
def dashboard(request):
    userProfile = None
    orders_count = None
    try:
        orders_count = Order.objects.filter(
            user=request.user, is_ordered=True).count()
        userProfile = UserProfile.objects.get(user=request.user)
    except:
        pass
    return render(request, "accounts/dashboard.html", context={'orders_count': orders_count, 'userProfile': userProfile})


def forgetPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        my_user = MyUser.objects.filter(email=email).exists()
        if my_user:
            user = MyUser.objects.get(email=email)
            # Generate verification code
            verification_code = default_token_generator.make_token(user)

            # Send email with verification link
            subject = 'Reset Email'
            current_site = get_current_site(request)
            message = render_to_string('accounts/resetEmail.html', {
                'user': user,
                'domain': current_site,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'verification_code': verification_code,
            })
            messages.success(request, "check your mail")
            to_email = user.email
            send_mail = EmailMessage(subject, message, to=[to_email])
            send_mail.send()

    return render(request, "accounts/forgetPassword.html")


def changePassword(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        return redirect('savePassword')
    else:
        messages.error(request, "Expired Link")
        return redirect("forgetPassword")


def savePassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            id = request.session['uid']
            user = MyUser.objects.get(id=id)
            user.set_password(password)
            user.save()
            messages.success(request, "password successfully change")
            return redirect("login")
        else:
            messages.warning(request, "password does't match")
            return redirect("savePassword")

    return render(request, "accounts/savePassword.html")


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user, is_ordered=True)
    return render(request, "accounts/my_orders.html", context={"orders": orders})


@login_required(login_url="login")
def order_details(request, order_id):
    order = Order.objects.get(
        user=request.user, order_number=order_id)
    order_product = OrderProduct.objects.filter(
        user=request.user, order__order_number=order_id)

    return render(request, "accounts/order_details.html", context={'order': order, 'order_product': order_product})


@login_required(login_url="login")
def edit_profile(request):
    userProfileExits = UserProfile.objects.filter(user=request.user).exists()

    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':

        if userProfileExits:
            user_form = UserForm(request.POST, instance=request.user)
            userProfile = get_object_or_404(UserProfile, user=request.user)
            user_profile = UserProfileForm(
                request.POST, request.FILES, instance=userProfile)

            if user_profile.is_valid() and user_form.is_valid():
                user_form.save()
                user_profile.save()
                messages.success(request, "Update Data Successfully")
                return redirect(url)
            else:
                messages.error(request, "Invalid Information")

        else:
            userProfileCre = UserProfile()
            my_user = MyUser.objects.get(id=request.user.id)
            userProfileCre.user = request.user
            if request.FILES.get('profile_image'):
                userProfileCre.profile_image = request.FILES.get(
                    'profile_image')
            userProfileCre.address_line_1 = request.POST['address_line_1']
            userProfileCre.address_line_2 = request.POST['address_line_2']
            userProfileCre.city = request.POST['city']
            userProfileCre.state = request.POST['state']
            userProfileCre.country = request.POST['country']

            my_user.first_name = request.POST['first_name']
            my_user.last_name = request.POST['last_name']
            my_user.phone = request.POST['phone']

            my_user.save()
            userProfileCre.save()

            return redirect(url)

    else:
        if userProfileExits:
            userProfile = get_object_or_404(UserProfile, user=request.user)
            user_profile = UserProfileForm(instance=userProfile)
            user_form = UserForm(instance=request.user)

        else:
            user_profile = UserProfileForm()
            user_form = UserForm(instance=request.user)
            userProfile = None

    return render(request, "accounts/edit_profile.html", context={"user_profile": user_profile, "user_form": user_form, "userProfile": userProfile})


@login_required(login_url="login")
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = MyUser.objects.get(username__exact=request.user.username)

        password_match = check_password(
            current_password, request.user.password)
        if password_match:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password Change Successfully")
                return redirect("change_password")
            else:
                messages.error(request, "Password Does not match")
        else:
            messages.error(request, "Invalid Password")

    return render(request, "accounts/change_password.html")
