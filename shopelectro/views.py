"""
Shopelectro views.

NOTE: They all should be 'zero-logic'. All logic should live in respective applications.
"""
from functools import wraps

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template.loader import render_to_string

from ecommerce import mailer
from ecommerce.cart import Cart
from ecommerce.models import Order
from ecommerce.forms import OrderForm
from . import config
from .models import Product
from blog.models import Post, get_crumbs as blog_crumbs
from catalog.models import Category, get_crumbs as catalog_crumbs


def cart_modifier(fn):
    """
    Decorator for cart's operations.

    Perform operations on Cart (e.g. remove, add) and always return JsonResponse in following format:
    {
        'cart': rendered_html_for_header_cart, // (see ecommerce/cart_dropdown.html template)
        'table': rendered_html_for_table_in_order_page, // (see ecommerce/order_table_form.html template)
    }

    Rationale: this decorator allows us to keep JS code logic-less and state-less.
    We simply get new html every time we hit backend,
    since the difference between returning HttpResponse('ok') and JsonResponse of two keys is insignificant.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Here we perform operation on Cart and return request object object.
        request = fn(*args, **kwargs)
        cart = Cart(request.session)
        header = render_to_string(
            'ecommerce/cart_dropdown.html', {'cart': cart}, request=request)
        table = render_to_string(
            'ecommerce/order_table_form.html', {'cart': cart, 'form': OrderForm()}, request=request)
        return JsonResponse({'cart': header, 'table': table})
    return wrapper


def save_order_to_session(session, order):
    session['order_id'] = order.id
    session.modified = True


@ensure_csrf_cookie
def index(request):
    """
    Main page view: root categories, top products.
    """

    top_products = Product.objects.filter(id__in=config.TOP_PRODUCTS)

    context = {
        'meta': config.page_metadata('main'),
        'category_tile': config.MAIN_PAGE_TILE,
        'footer_links': config.FOOTER_LINKS,
        'href': config.HREFS,
        'top_products': top_products,
    }

    return render(
        request, 'index/index.html', context)


@ensure_csrf_cookie
def category_page(request, category_slug, sorting=0):
    """
    Category page: all it's subcategories and products.

    :param sorting: preferred sorting index from CATEGORY_SORTING tuple
    :param category_slug: given category's slug
    :param request: HttpRequest object
    :return:
    """

    sorting = int(sorting)
    sorting_option = config.category_sorting(sorting)

    # if there is no view_type specified, default will be tile
    view_type = request.session.get('view_type', 'tile')
    category = get_object_or_404(Category.objects, slug=category_slug)
    products, total_count = category.get_recursive_products_with_count(
        sorting=sorting_option)

    context = {
        'category': category,
        'products': products,
        'total_products': total_count,
        'sorting_options': config.category_sorting(),
        'sort': sorting,
        'breadcrumbs': catalog_crumbs(category),
        'view_type': view_type
    }

    return render(request, 'catalog/category.html', context)


@ensure_csrf_cookie
def product_page(request, product_id):
    """
    Product page.

    :param product_id: given product's id
    :param request: HttpRequest object
    :return:
    """

    product = get_object_or_404(Product.objects, id=product_id)
    images = product.images
    main_image = settings.IMAGE_THUMBNAIL

    if images:
        main_image = [image for image in images if image.find('main') != -1][0]

    context = {
        'breadcrumbs': catalog_crumbs(product),
        'images': images,
        'main_image': main_image,
        'product': product,
    }

    return render(request, 'catalog/product.html', context)


def load_more(request, category_slug, offset=0, sorting=0):
    """
    Loads more products of a given category.

    :param sorting: preferred sorting index from CATEGORY_SORTING tuple
    :param request: HttpRequest object
    :param category_slug: Slug for a given category
    :param offset: used for slicing QuerySet.
    :return:
    """

    category = get_object_or_404(Category.objects, slug=category_slug)
    sorting_option = config.category_sorting(int(sorting))
    products, _ = category.get_recursive_products_with_count(
        sorting=sorting_option, offset=int(offset))
    view = request.session.get('view_type', 'tile')

    return render(request, 'catalog/category_products.html',
                  {'products': products, 'view_type': view})


@require_POST
def set_view_type(request):
    """
    Simple 'view' for setting view type to user's session.
    Requires POST HTTP method, since it sets data to session.
    """

    request.session['view_type'] = request.POST['view_type']
    return HttpResponse('ok')  # Return 200 OK


def blog_post(request, type_=''):
    return render(request, 'blog/posts.html', {
        'posts': Post.objects.filter(type=type_),
        'breadcrumbs': blog_crumbs(settings.CRUMBS['blog']),
        'page': config.page_metadata(type_),
    })


def get_models_names(model_type, search_term):
    """
    Returns related names for models.
    """

    return model_type.objects.filter(name__contains=search_term).values('name')


def admin_autocomplete(request):
    """
    Returns autocompleted names as response.
    """

    model_map = {'product': Product, 'category': Category}
    search_term = request.GET['q']
    page_term = request.GET['pageType']

    if page_term not in ['product', 'category']:
        return

    query_objects = get_models_names(model_map[page_term], search_term)
    names = [item['name'] for item in query_objects]

    return JsonResponse(names, safe=False)


@cart_modifier
@require_POST
def add_to_cart(request):
    """
    View to add product to cart.
    Requires POST method.
    Return request as every other @cart_modifier function.
    """
    cart = Cart(request.session)
    product = get_object_or_404(Product, id=request.POST['product'])
    cart.add(product, request.POST['quantity'])
    return request


@cart_modifier
@require_POST
def change_count_in_cart(request):
    """
    Change count
    :param request:
    :return:
    """
    cart = Cart(request.session)
    product = get_object_or_404(Product, id=request.POST['product'])
    cart.change_product_quantity(product, request.POST['quantity'])
    return request


@cart_modifier
@require_POST
def cart_flush(request):
    cart = Cart(request.session)
    cart.clear()
    return request


@cart_modifier
@require_POST
def cart_remove(request):
    cart = Cart(request.session)
    product = get_object_or_404(Product, id=request.POST['product'])
    cart.remove(product)
    return request


@require_POST
def one_click_buy(request):
    Cart(request.session).clear()

    cart = Cart(request.session)
    product = get_object_or_404(Product, id=request.POST['product'])
    cart.add(product, request.POST['quantity'])
    order = Order(phone=request.POST['phone'])
    order.set_items(cart)
    save_order_to_session(request.session, order)
    mailer.send_order(subject=config.EMAIL_SUBJECTS['order'], order=order, to_customer=False)
    return HttpResponse('ok')


@require_POST
def order_call(request):
    phone, time, url = request.POST['phone'], request.POST['time'], request.POST['url']
    mailer.order_call(config.EMAIL_SUBJECTS['call'], phone, time, url)
    return HttpResponse('ok')


def success_order(request):
    order_id = request.session['order_id']
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'ecommerce/success.html', {'order': order})


def order_page(request):
    """Order page with order content's table and proceeding form."""
    def save_order(form):
        """Saves order to DB and to session."""
        order = form.save()
        order.set_items(cart)
        cart.clear()
        save_order_to_session(request.session, order)
        return order

    cart = Cart(request.session)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = save_order(form)
            mailer.send_order(subject=config.EMAIL_SUBJECTS['order'], order=order, to_customer=True)
            return redirect('order_success')
    else:
        form = OrderForm()
    return render(request,
                  'ecommerce/order.html',
                  {'cart': cart, 'form': form})
