from django.core.cache import cache
from app_marketplace.models import CategoryModel, CartModel
from app_marketplace.services import ComparedProductsListService, AddItemToCart
from marketplace.settings import CATEGORIES_CACHE_TIME
from django.contrib.auth.models import AnonymousUser
from .cart import Cart


def categories(request):
    category_list = cache.get('categories')
    if category_list is None:
        category_list = CategoryModel.objects.filter(is_active=True)
        cache.set('categories', category_list, CATEGORIES_CACHE_TIME)
    return {'categories': category_list}


def total_compared_items(request):
    out = len(ComparedProductsListService.get_compared_list(request))
    return {'total_compared_items': out}


def cart_information(request):
    count_product_in_cart = 0
    total_price_cart = 0
    if not isinstance(request.user, AnonymousUser):
        cart = CartModel.objects.filter(
            user=request.user, status='actively'
        ).first()
        if cart is not None:
            count_product_in_cart = AddItemToCart.get_products_count(cart=cart)
            total_price_cart = AddItemToCart.get_cart_prices(cart=cart)
    else:
        cart = Cart(request)
        count_product_in_cart = cart.__len__()
        total_price_cart = cart.get_total_price()

    return {
        'count_product_in_cart': count_product_in_cart,
        'total_price_cart': total_price_cart
    }

