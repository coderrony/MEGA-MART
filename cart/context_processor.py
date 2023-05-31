from cart.models import CartItem, Cart
from .views import _get_session


def get_total(request):

    total = 0
    try:
        if request.user.is_authenticated:
            cartItem = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_get_session(request))
            cartItem = CartItem.objects.filter(cart=cart)

        for i in cartItem:
            total += i.quantity
    except:
        total = 0

    return dict(totalQuantity=total)
