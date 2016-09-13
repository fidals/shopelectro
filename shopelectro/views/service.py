"""
Shopelectro's service views.
"""
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from ecommerce import mailer
from ecommerce.models import Order
from ecommerce.views import get_keys_from_post

from shopelectro.models import Order


def test_yandex(request):
    # TODO: remove when Yandex-integration will be tested
    return HttpResponse(request)


@csrf_exempt
def yandex_check(request):
    """
    Handle Yandex check.

    We simply accept every check.
    It's marked with @csrf_exempt, because we don't need
    to check CSRF in yandex-requests.
    """
    return render(request,
                  'ecommerce/yandex_check.xml',
                  {'invoice': request.POST['invoiceId']},
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

    def first_aviso(order):
        return not order.paid

    def send_mail_to_se(order):
        paid, profit = get_keys_from_post(request,
                                          'orderSumAmount',
                                          'shopSumAmount')
        commission = 100 * float(paid) / float(profit)
        mailer.send_order(template='ecommerce/yandex_order_email.html',
                          subject=settings.EMAIL_SUBJECTS['yandex_order'],
                          order=order,
                          to_customer=False,
                          extra_context={
                              'paid': paid,
                              'profit': profit,
                              'comission': commission})

    def send_mail_to_customer(order):
        mailer.send_order(subject=settings.EMAIL_SUBJECTS['yandex_order'],
                          order=order,
                          to_shop=False)

    order = get_object_or_404(Order, pk=request.POST['orderNumber'])

    if first_aviso(order):
        order.paid = True
        send_mail_to_customer(order)
        send_mail_to_se(order)

    invoice_id = request.POST['invoiceId']
    return render(request,
                  'ecommerce/yandex_aviso.xml',
                  {'invoice': invoice_id},
                  content_type='application/xhtml+xml')


@require_POST
@csrf_exempt
def ya_feedback_request(request):
    """Send email to user with Я.Маркет feedback request"""
    mailer.ya_feedback()

    return render(request, 'ecommerce/yandex_feedback_success.html',
                  {'email': request.POST['email']})


def ya_feedback_with_redirect(request):
    """Redirect user to Я.Маркет for feedback"""
    return render(request, 'ecommerce/yandex_feedback_redirect.html')
