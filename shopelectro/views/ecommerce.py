"""
Shopelectro's ecommerce views.

NOTE: They all should be 'zero-logic'.
All logic should live in respective applications.
"""
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ecommerce import mailer
from ecommerce.cart import Cart
from ecommerce.models import Order
from ecommerce import views as ec_views
from ecommerce.views import get_keys_from_post, save_order_to_session

from shopelectro.models import Product, Order
from shopelectro.cart import WholesaleCart
from shopelectro.forms import OrderForm


# ECOMMERCE VIEWS
class OrderPage(ec_views.OrderPage):
    order_form = OrderForm


class AddToCart(ec_views.AddToCart):
    cart = WholesaleCart
    order_form = OrderForm


class RemoveFromCart(ec_views.RemoveFromCart):
    cart = WholesaleCart
    order_form = OrderForm


class ChangeCount(ec_views.ChangeCount):
    cart = WholesaleCart
    order_form = OrderForm


class FlushCart(ec_views.FlushCart):
    order_form = OrderForm


class SuccessOrder(ec_views.SuccessOrder):
    order = Order


@require_POST
def one_click_buy(request):
    """
    Handle one-click-buy.

    Accept XHR, save Order to DB, send mail about it
    and return 200 OK.
    """
    Cart(request.session).clear()

    cart = Cart(request.session)
    product = get_object_or_404(Product, id=request.POST['product'])
    cart.add(product, int(request.POST['quantity']))
    order = Order(phone=request.POST['phone'])
    order.set_positions(cart)
    save_order_to_session(request.session, order)
    mailer.send_order(subject=settings.EMAIL_SUBJECTS['order'],
                      order=order,
                      to_customer=False)
    return HttpResponse('ok')


@require_POST
def order_call(request):
    """Send email about ordered call."""
    phone, time, url = get_keys_from_post(request, 'phone', 'time', 'url')
    mailer.order_call(subject=settings.EMAIL_SUBJECTS['call'],
                      phone=phone,
                      time=time,
                      url=url)
    return HttpResponse('ok')


def yandex_order(request):
    """
    Handle yandex order: order with yandex-provided payment system.

    Save cart from user session as an Order, return order_id.
    """
    cart = Cart(request.session)
    name, phone, email = get_keys_from_post(request, 'name', 'phone', 'email')
    order = Order(name=name, phone=phone, email=email)
    order.set_positions(cart)
    return HttpResponse(order.id)
