"""
Shopelectro helpers functions and views.
"""
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from shopelectro.models import Product, Category
from pages.models import Page


# Sets CSRF-cookie to CBVs.
set_csrf_cookie = method_decorator(ensure_csrf_cookie, name='dispatch')


MODEL_MAP = {'product': Product, 'category': Category, 'page': Page}


@require_POST
def set_view_type(request):
    """
    Simple 'view' for setting view type to user's session.
    Requires POST HTTP method, since it sets data to session.
    """

    request.session['view_type'] = request.POST['view_type']
    return HttpResponse('ok')  # Return 200 OK
