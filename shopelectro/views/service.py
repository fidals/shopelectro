import logging
from hashlib import md5

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ecommerce import mailer
from ecommerce.views import get_keys_from_post

from shopelectro.models import Order

logger = logging.getLogger(__name__)


YANDEX_REQUEST_PARAM = (
    'action', 'orderSumAmount', 'orderSumCurrencyPaycash', 'orderSumBankPaycash',
    'shopId', 'invoiceId', 'customerNumber'
)


def generate_md5_for_ya_kassa(post_body):
    """Generate md5 based on this param."""
    params = [post_body[param] for param in YANDEX_REQUEST_PARAM]
    params.append(settings.YANDEX_SHOP_PASS)
    param_sequence = str(';'.join(params)).encode('utf-8')
    return md5(param_sequence).hexdigest().upper()


def has_correct_md5(post_body):
    """Compare our md5 with md5 from yandex request."""
    md5 = generate_md5_for_ya_kassa(post_body)
    return md5 == post_body['md5']


@csrf_exempt
def yandex_check(request):
    """
    Handle Yandex check.

    We simply accept every check.
    It's marked with @csrf_exempt, because we don't need
    to check CSRF in yandex-requests.
    """
    return render(request, 'ecommerce/yandex_check.xml', {'invoice': request.POST['invoiceId']},
                  content_type='application/xhtml+xml')


@csrf_exempt
def yandex_aviso(request):
    """
    Handle Yandex Aviso check.

    It's marked with @csrf_exempt, because we don't need to
    check CSRF in yandex-requests.

    1. Retrieve order number from request, find in in DB.
    2. If it's a first aviso check (there might be more than one,
       depends on Yandex)
       send different emails to client and shop.
    3. Get invoice id from request and return XML to Yandex.
    """
    def is_first_aviso(order_):
        return order_ and not order_.paid

    def send_mail_to_shop(order):
        paid, profit = get_keys_from_post(request, 'orderSumAmount', 'shopSumAmount')
        proportion = 100 * float(profit) / float(paid)
        commission = round(100 - proportion, 2)  # in percents
        mailer.send_order(
            template='ecommerce/yandex_order_email.html',
            subject=settings.EMAIL_SUBJECTS['yandex_order'],
            order=order,
            to_customer=False,
            extra_context={
                'paid': paid,
                'profit': profit,
                'commission': commission,
                # see se.OrderPage class for a detail about `shop` context.
                'shop': settings.SHOP,
            })

    def send_mail_to_customer(order):
        mailer.send_order(
            subject=settings.EMAIL_SUBJECTS['yandex_order'],
            order=order,
            to_shop=False,
            # see se.OrderPage class for a detail about `shop` context.
            extra_context={'shop': settings.SHOP},
        )

    if not has_correct_md5(request.POST):
        return render(
            request, 'ecommerce/yandex_aviso.xml',
            content_type='application/xhtml+xml'
        )

    logger.info(f'received yandex aviso. Aviso data: {request.POST}')

    # maybe we can include django-annoying for such cases
    # https://github.com/skorokithakis/django-annoying#get_object_or_none-function
    try:
        order = Order.objects.get(pk=request.POST['customerNumber'])
    except Order.DoesNotExist:
        order = None

    if is_first_aviso(order):
        order.paid = True
        send_mail_to_customer(order)
        send_mail_to_shop(order)
        order.save()

    invoice_id = request.POST['invoiceId']
    return render(request, 'ecommerce/yandex_aviso.xml', {'invoice': invoice_id},
                  content_type='application/xhtml+xml')


@require_POST
@csrf_exempt
def ya_feedback_request(request):
    """Send email to user with Y.Market feedback request."""
    user_email = request.POST['email']
    mailer.ya_feedback(user_email)

    return render(request, 'ecommerce/yandex_feedback_success.html',
                  {'email': user_email})


def ya_feedback_with_redirect(request):
    """Redirect user to Y.Market for feedback."""
    return render(request, 'ecommerce/yandex_feedback_redirect.html')
