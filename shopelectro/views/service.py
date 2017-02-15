"""
Shopelectro's service views.
"""
import os
import sys
import logging
from hashlib import md5
from functools import wraps

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ecommerce import mailer
from ecommerce.views import get_keys_from_post

from shopelectro.models import Order


def logging_yandex_kassa(func):
    @wraps(func)
    def make_logging(*args, **kwargs):
        file_name = os.path.join(settings.BASE_DIR, 'yandex_kassa.log')
        conf_for_logger = logging.basicConfig(
            filename=file_name, level=logging.DEBUG, format='\n %(asctime)s \n %(message)s \n')
        logger = logging.getLogger(conf_for_logger)
        response = None

        try:
            logger.info('REQUEST_ROUTE: {}\n REQUEST_BODY: {}'.format(args[0].path, args[0].POST))
            response = func(*args, **kwargs)
            response_code = response.status_code
            response_content = str(response.content)

            if not response_code == 200 or 'code="0"' not in response_content:
                logger.warning('STATUS_CODE: {}\n RESPONSE_CONTENT: {}'.format(
                    response_code, response_content))

            logger.info('STATUS_CODE: {}\n RESPONSE_CONTENT: {}'.format(
                    response_code, response_content))
        except:
            logger.warning('ERROR: \n {}'.format(sys.exc_info()))

        return response

    return make_logging

YANDEX_REQUEST_PARAM = (
    'action', 'orderSumAmount', 'orderSumCurrencyPaycash', 'orderSumBankPaycash',
    'shopId', 'invoiceId', 'customerNumber'
)


def generate_md5_for_ya_kassa(post_body):
    """
    Generate md5 based on this param
    """
    params = [post_body[param] for param in YANDEX_REQUEST_PARAM]
    params.append(settings.YANDEX_SHOP_PASS)
    param_sequence = str(';'.join(params)).encode('utf-8')
    return md5(param_sequence).hexdigest().upper()


def has_correct_md5(post_body):
    """
    Compare our md5 with md5 from yandex request
    """
    md5 = generate_md5_for_ya_kassa(post_body)
    return md5 == post_body['md5']


@logging_yandex_kassa
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


@logging_yandex_kassa
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
        commission = round((float(paid) - float(profit)) / float(paid), 2)
        mailer.send_order(
            template='ecommerce/yandex_order_email.html',
            subject=settings.EMAIL_SUBJECTS['yandex_order'],
            order=order,
            to_customer=False,
            extra_context={
                'paid': paid,
                'profit': profit,
                'commission': commission
            })

    def send_mail_to_customer(order):
        mailer.send_order(
            subject=settings.EMAIL_SUBJECTS['yandex_order'], order=order, to_shop=False)

    if not has_correct_md5(request.POST):
        return render(
            request, 'ecommerce/yandex_aviso.xml',
            content_type='application/xhtml+xml'
        )

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
    """Send email to user with Y.Market feedback request"""
    user_email = request.POST['email']
    mailer.ya_feedback(user_email)

    return render(request, 'ecommerce/yandex_feedback_success.html',
                  {'email': user_email})


def ya_feedback_with_redirect(request):
    """Redirect user to Y.Market for feedback"""
    return render(request, 'ecommerce/yandex_feedback_redirect.html')
