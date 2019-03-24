import json

from django.conf import settings
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import etag, require_POST
from django.utils.http import quote_etag

from ecommerce import mailer, views as ec_views
from pages.models import CustomPage

from shopelectro.cart import SECart
from shopelectro.forms import OrderForm
from shopelectro.models import Product, Order


# ECOMMERCE VIEWS
class OrderPage(ec_views.OrderPage):
    order_form = OrderForm
    cart = SECart
    # Django does not provide context_processors for render_to_string function,
    # which is used to render an order mail. So we have to explicitly pass
    # a context to it.
    email_extra_context = {'shop': settings.SHOP}

    def get_context_data(self, request, **kwargs):
        data = super().get_context_data(request, **kwargs)
        return {
            **data,
            'page': CustomPage.objects.get(slug='order'),
            'raw_order_fields': json.dumps({
                field.html_name: f'#{field.id_for_label}' for field in data['form']
            }),
        }


# @todo #789:60m Make cart routes REST style instead of RPC.

# @todo #789:15m Test http cache for cart-get route.


def cart_etag(request):
    cart = SECart(request.session)
    positions = ','.join(f'{id}:{pos["quantity"]}' for id, pos in cart)
    return quote_etag(f'{len(cart)}={positions}')


class Cart(ec_views.CartModifier):

    cart = SECart
    position_model = Product
    order_form = OrderForm

    def get(self, request):
        return self.json_response(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        # Prevent django cache middleware to add default max-age
        # this view should always revalidate a request.
        force_revalidate = cache_control(max_age=0, must_revalidate=True)
        # Add ETag for revalidation
        etag_hasher = etag(cart_etag)
        view = super().as_view(*args, **kwargs)
        return force_revalidate(etag_hasher(view))


class AddToCart(ec_views.AddToCart):
    cart = SECart
    position_model = Product
    order_form = OrderForm


class RemoveFromCart(ec_views.RemoveFromCart):
    cart = SECart
    position_model = Product
    order_form = OrderForm


class ChangeCount(ec_views.ChangeCount):
    cart = SECart
    position_model = Product
    order_form = OrderForm


class FlushCart(ec_views.FlushCart):
    position_model = Product
    order_form = OrderForm


class OrderSuccess(ec_views.OrderSuccess):

    order = Order.objects.all().prefetch_related('positions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context['order']
        positions_json = serializers.serialize(
            'json', order.positions.all(), fields=['name', 'quantity', 'price'],
        )

        return {
            **context,
            'positions_json': positions_json,
            'total_revenue': order.revenue,
        }


@require_POST
def one_click_buy(request):
    """
    Handle one-click-buy.

    Accept XHR, save Order to DB, send mail about it
    and return 200 OK.
    """
    cart = SECart(request.session)
    cart.clear()

    product = get_object_or_404(Product, id=request.POST['product'])
    cart.add(product, int(request.POST['quantity']))
    order = Order(phone=request.POST['phone'])
    order.set_positions(cart)
    ec_views.save_order_to_session(request.session, order)
    mailer.send_order(
        subject=settings.EMAIL_SUBJECTS['one_click'],
        order=order,
        to_customer=False,
        # see se.OrderPage class for a detail about `shop` context.
        extra_context={'shop': settings.SHOP},
    )
    return HttpResponse('ok')


@require_POST
def order_call(request):
    """Send email about ordered call."""
    phone, time, url = ec_views.get_keys_from_post(
        request, 'phone', 'time', 'url')

    mailer.send_backcall(
        subject=settings.EMAIL_SUBJECTS['call'],
        phone=phone,
        time=time,
        url=url,
    )

    return HttpResponse('ok')


class YandexOrder(OrderPage):

    def post(self, request):
        cart = self.cart(request.session)
        form = self.order_form(request.POST)
        if not form.is_valid():
            return render(request, self.template, {'cart': cart, 'form': form})

        order = form.save()
        order.set_positions(cart)
        ec_views.save_order_to_session(request.session, order)

        # Took form fields from Yandex docs https://goo.gl/afKfsz
        response_data = {
            'yandex_kassa_link': settings.YANDEX_KASSA_LINK,  # Required
            'shopId': settings.SHOP['id'],  # Required
            'scid': settings.SHOP['scid'],  # Required
            'shopSuccessURL': settings.SHOP['success_url'],
            'shopFailURL': settings.SHOP['fail_url'],
            'customerNumber': order.id,  # Required
            'sum': order.total_price,  # Required
            'orderNumber': order.fake_order_number,
            'cps_phone': order.phone,
            'cps_email': order.email,
            'paymentType': request.POST.get('payment_type'),
        }

        return JsonResponse(response_data)
