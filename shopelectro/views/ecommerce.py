"""
Shopelectro's ecommerce views.

NOTE: They all should be 'zero-logic'.
All logic should live in respective applications.
"""
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from ecommerce import mailer, views as ec_views
from ecommerce.cart import Cart
from ecommerce.models import Order

from shopelectro.cart import WholesaleCart
from shopelectro.forms import OrderForm
from shopelectro.models import Product, Order


# ECOMMERCE VIEWS
class OrderPage(ec_views.OrderPage):
    order_form = OrderForm


class AddToCart(ec_views.AddToCart):
    cart = WholesaleCart
    product_model = Product
    order_form = OrderForm


class RemoveFromCart(ec_views.RemoveFromCart):
    cart = WholesaleCart
    product_model = Product
    order_form = OrderForm


class ChangeCount(ec_views.ChangeCount):
    cart = WholesaleCart
    product_model = Product
    order_form = OrderForm


class FlushCart(ec_views.FlushCart):
    product_model = Product
    order_form = OrderForm


class OrderSuccess(ec_views.OrderSuccess):
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
    ec_views.save_order_to_session(request.session, order)
    mailer.send_order(
        subject=settings.EMAIL_SUBJECTS['order'],
        order=order, to_customer=False
    )
    return HttpResponse('ok')


@require_POST
def order_call(request):
    """Send email about ordered call."""
    phone, time, url = ec_views.get_keys_from_post(request, 'phone', 'time', 'url')

    mailer.order_backcall(
        subject=settings.EMAIL_SUBJECTS['call'],
        phone=phone, time=time, url=url
    )

    return HttpResponse('ok')


class YandexOrder(OrderPage):
    def post(self, request):
        request.POST = request.POST.dict()

        cart = self.cart(request.session)
        form = self.order_form(request.POST)

        if not form.is_valid():
            return render(request, self.template, {'cart': cart, 'form': form})

        order = form.save()
        order.set_positions(cart)
        ec_views.save_order_to_session(request.session, order)

        # Took form fields from Yandex docs https://goo.gl/afKfsz
        response_data = {
            'yandex_kassa_link': settings.YANDEX_KASSA_LINK, # Required
            'shopId': settings.SHOP['id'],  # Required
            'scid': settings.SHOP['scid'],  # Required
            'shopSuccessURL': settings.SHOP['success_url'],
            'shopFailURL': settings.SHOP['fail_url'],
            'customerNumber': order.id, # Required
            'sum': order.total_price, # Required
            'orderNumber': order.fake_order_number,
            'cps_phone': order.phone,
            'cps_email': order.email,
            'paymentType': request.POST.get('payment_type'),
        }

        return JsonResponse(response_data)
