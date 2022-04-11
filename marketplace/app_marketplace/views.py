from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.models import Q, Count
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import View, generic
from django.views.generic import DetailView, TemplateView, FormView, ListView
from app_marketplace.forms import (
    ClearCacheForm, CreateOrderDeliveryForm,
    CreateOrderPaymentForm, CreatePaymentForm
)
from app_marketplace.models import (
    ShopModel, ProductOnShopModel, BannerModel, ProductModel, CartModel,
    TagsModel, CartProductModel, User, OrderModel, DiscountModel,
    CategoryModel
)
from app_marketplace.services import (
    HomePageService, CatalogService, AddCommentToProductService,
    AddItemToCart, GetDiscountsForProductsService, ComparedProductsListService,
    AddLookedProductsService, PaymentService
)
from app_marketplace.utils import clear_cache
from app_users.views import RegistrationView
from marketplace import settings
from .cart import Cart
import random
from django.utils import timezone
from datetime import date, timedelta

cached_time = settings.CACHED_TIME


class MainPageView(TemplateView):
    """Представление, отображающее главную страницу."""
    template_name = 'app_marketplace/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = CategoryModel.objects.all().select_related().filter(
            is_active=True)[:3]

        # Устанавливаем кэш для баннеров
        if 'banners' not in cache:
            banner_list = BannerModel.objects.select_related(
                'shop_product').filter(is_active=True).order_by('?')[:3]
            cache.set('banners', banner_list, cached_time)
        else:
            banner_list = cache.get('banners')

        # Устанавливаем кэш для товара "Предложения дня"
        offer_of_day_price = None
        if 'offer_of_day' not in cache:
            offer_of_day = HomePageService.get_random_product()
            if offer_of_day:
                cache.set('offer_of_day', offer_of_day, cached_time)
                offer_of_day_price, discount = \
                    GetDiscountsForProductsService.get_discount_price(
                        product=offer_of_day, price=offer_of_day.min_price)
                if discount:
                    cache.set('offer_of_day_price', offer_of_day_price,
                              cached_time)
        else:
            offer_of_day = cache.get('offer_of_day')
            offer_of_day_price = cache.get('offer_of_day_price')

        # Устанавливаем кэш для популярных товаров
        top_products = None
        if 'top_products' not in cache:
            top_goods_list = HomePageService.get_top_products()
            if all(top_goods_list.values()):
                top_products = []
                for product, product_on_shop in top_goods_list.items():
                    discount_price, discount = \
                        GetDiscountsForProductsService.get_discount_price(
                            product=product, price=product_on_shop.price
                        )
                    if discount:
                        top_products.append(
                            ((discount_price, discount, product_on_shop.price),
                             product,
                             product_on_shop.pk)
                        )
                    else:
                        top_products.append(
                            ((product_on_shop.price, None, None),
                             product,
                             product_on_shop.pk)
                        )
                cache.set('top_products', top_products, cached_time)
                del top_goods_list
        else:
            top_products = cache.get('top_products')

        # Устанавливаем кэш для товаров со скидкой ("Горячие предложения")
        hot_products = None
        if 'hot_products' not in cache:
            hot_products_list = HomePageService.get_hot_offers()
            if len(hot_products_list):
                hot_products = []
                for product, product_on_shop in hot_products_list.items():
                    discount_price, discount = \
                        GetDiscountsForProductsService.get_discount_price(
                            product=product, price=product_on_shop.price
                        )
                    if discount:
                        hot_products.append(
                            (
                                (
                                    discount_price,
                                    discount,
                                    product_on_shop.price
                                ),
                                product,
                                product_on_shop.pk
                            )
                        )
                    else:
                        hot_products.append(
                            (
                                (
                                    product_on_shop.price,
                                    None,
                                    None
                                ),
                                product,
                                product_on_shop.pk
                            )
                        )
                cache.set('hot_products', hot_products, cached_time)
                del hot_products_list
        else:
            hot_products = cache.get('hot_products')

        # Устанавливаем кэш для товаров с ограниченным тиражом
        limited_products = None
        if 'limited_products' not in cache:
            if offer_of_day:
                limited_products_list = HomePageService.get_limited_products(
                    offer_of_day
                )
                if len(limited_products_list):
                    limited_products = []
                    for product, product_on_shop in \
                            limited_products_list.items():
                        discount_price, discount = \
                            GetDiscountsForProductsService.get_discount_price(
                                product=product, price=product_on_shop.price
                            )
                        if discount:
                            limited_products.append(
                                (
                                    (
                                        discount_price,
                                        discount,
                                        product_on_shop.price
                                    ),
                                    product,
                                    product_on_shop.pk
                                )
                            )
                        else:
                            limited_products.append(
                                (
                                    (
                                        product_on_shop.price,
                                        None,
                                        None
                                    ),
                                    product,
                                    product_on_shop.pk
                                )
                            )
                    cache.set(
                        'limited_products', limited_products, cached_time
                    )
                    del limited_products_list
        else:
            limited_products = cache.get('limited_products')

        today = date.today() + timedelta(days=2)
        today = today.strftime("%d.%m.%Y")

        context['banner_list'] = banner_list
        context['home_categories'] = category
        context['offer_of_day'] = offer_of_day
        context['offer_of_day_price'] = offer_of_day_price
        context['top_products'] = top_products
        context['hot_products'] = hot_products
        context['limited_products'] = limited_products
        context['date'] = today
        return context

    def post(self, request, *args, **kwargs):
        if 'compare' in request.POST.keys():
            product_on_shop_id = request.POST.get('compare')
            product = ProductModel.objects.filter(
                product_on_shop__pk=product_on_shop_id
            ).first()
            if product:
                return ComparedProductsListService.add_item_to_cookies(
                    request=request,
                    product=product,
                    product_on_shop_id=product_on_shop_id
                )
        return HttpResponseRedirect(request.path)


class ShopDetailView(DetailView):
    """Представление, отображающее страницу о магазине."""
    model = ShopModel
    template_name = 'app_marketplace/shop_details.html'
    context_object_name = 'shop'

    def get_queryset(self):
        # Устанавливаем кэш для текущего магазина
        shop_cache_key = 'shop:{}'.format(self.kwargs['slug'])
        if shop_cache_key not in cache:
            queryset = ShopModel.objects.filter(
                slug=self.kwargs['slug']
            ).select_related('image')
            cache.set(shop_cache_key, queryset, cached_time)
        else:
            queryset = cache.get(shop_cache_key)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        shop_products = ProductOnShopModel.objects.filter(
            product__is_active=True, shop=context.get('shop'), for_sale=True
        ).select_related('product').order_by('-product__view_count')[:10]
        shop_products_discount_prices = [
            GetDiscountsForProductsService.get_discount_price(
                product=shop_product.product,
                price=shop_product.price
            )
            if len(GetDiscountsForProductsService.get_discounts(
                shop_product.product)) else (None, None)
            for shop_product in shop_products
        ]
        context['shop_products'] = list(
            zip(shop_products, shop_products_discount_prices)
        )
        return context

    def post(self, request, *args, **kwargs):
        if 'compare' in request.POST.keys():
            product_on_shop_id = request.POST.get('compare')
            product = ProductModel.objects.filter(
                product_on_shop__pk=product_on_shop_id).first()
            if product:
                return ComparedProductsListService.add_item_to_cookies(
                    request=request, product=product,
                    product_on_shop_id=product_on_shop_id
                )
        return HttpResponseRedirect(request.path)


class ProductDetailView(DetailView):
    """Представление, отображающее детальную информацию о товаре."""
    model = ProductModel
    template_name = 'app_marketplace/product_details.html'
    context_object_name = 'product'

    def get_queryset(self):
        # Устанавливаем кэш для текущего товара
        product_cache_key = 'product:{}'.format(self.kwargs['slug'])
        if product_cache_key not in cache:
            queryset = ProductModel.objects.filter(
                is_active=True, slug=self.kwargs['slug']
            ).select_related('main_image').prefetch_related('characteristics')
            cache.set(product_cache_key, queryset, cached_time)
        else:
            queryset = cache.get(product_cache_key)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        # Увеличиваем количество просмотров текущего товара
        product = context.get('product', None)
        product.view_count += 1
        product.save(update_fields=['view_count'])

        # Добавляем товар в список просмотренных товаров
        user = self.request.user
        if not isinstance(user, AnonymousUser):
            AddLookedProductsService.add_item_to_watch_list(
                user=user, product=product
            )

        # Устанавливаем кэш для тэгов текущего товара
        tags_cache_key = 'tags:{}'.format(self.kwargs['slug'])
        if tags_cache_key not in cache:
            context['tags'] = TagsModel.objects.filter(product=product)
            cache.set(tags_cache_key, context['tags'], cached_time)
        else:
            context['tags'] = cache.get(tags_cache_key)

        # Устанавливаем кэш для количества отзывов для текущего товара
        count_comments_cache_key = 'count_comments:{}'.format(
            self.kwargs['slug']
        )
        if count_comments_cache_key not in cache:
            context['count_comments'] = \
                AddCommentToProductService.get_review_count(product=product)
            cache.set(
                count_comments_cache_key,
                context['count_comments'],
                cached_time
            )
        else:
            context['count_comments'] = cache.get(count_comments_cache_key)

        # Устанавливаем кэш для отзывов для текущего товара
        all_comments_cache_key = 'all_comments_cache_key:{}'.format(
            self.kwargs['slug']
        )
        comments_cache_key = 'comments_cache_key:{}'.format(
            self.kwargs['slug']
        )
        if 'rewShowMore' in self.request.GET:
            if all_comments_cache_key not in cache:
                comments = AddCommentToProductService().get_review_list(
                    product=product
                )
                cache.set(all_comments_cache_key, comments, cached_time)
                context['comments'] = comments
            else:
                context['comments'] = cache.get(all_comments_cache_key)
        else:
            if comments_cache_key not in cache:
                comments = AddCommentToProductService().get_review_list(
                    product=product, count=2
                )
                cache.set(comments_cache_key, comments, cached_time)
                context['comments'] = comments
            else:
                context['comments'] = cache.get(comments_cache_key)

        # Устанавливаем кэш для списка с текущим товаром с данными о
        # продаже в разных магазинах
        product_on_shops_cache_key = 'product_on_shops:{}'.format(
            self.kwargs['slug']
        )
        min_price_cache_key = 'min_price_cache_key:{}'.format(
            self.kwargs['slug']
        )
        if product_on_shops_cache_key not in cache:
            min_price = 0

            # Получаем данные из базы
            product_on_shops = ProductOnShopModel.objects.filter(
                product=product, for_sale=True, quantity__gt=0
            ).select_related('shop', 'product')

            # Если товар продается, актуализируем цену с учетом скидок
            if len(product_on_shops):
                product_on_shops = [
                    (
                        GetDiscountsForProductsService.get_discount_price(
                            product=product.product, price=product.price
                        )
                        if product.product.discounts.exists() else (
                            product.price, None), product
                    )
                    for product in product_on_shops
                ]
                min_price = min(product_on_shops, key=lambda elem: elem[0][0])
                cache.set(
                    product_on_shops_cache_key, product_on_shops, cached_time
                )
                cache.set(min_price_cache_key, min_price, cached_time)
        else:
            product_on_shops = cache.get(product_on_shops_cache_key)
            min_price = cache.get(min_price_cache_key)

        context['product_on_shops'] = product_on_shops
        context['min_price'] = min_price
        context['title'] = product.model
        return context

    def post(self, request, *args, **kwargs):
        user = request.user

        if (
                not isinstance(user, AnonymousUser) and
                request.POST.get('review', False)
        ):
            product = ProductModel.objects.get(**kwargs)
            review = request.POST['review']
            user = request.user
            AddCommentToProductService().add_feedback(
                product=product, user=user, text=review
            )
        if 'compare' in request.POST.keys():
            product_on_shop_id = request.POST.get('compare')
            if product_on_shop_id.isdigit():
                return ComparedProductsListService.add_item_to_cookies(
                    request=request,
                    product=self.get_object(),
                    product_on_shop_id=product_on_shop_id
                )
        return HttpResponseRedirect(redirect_to=request.path)


class DynamicAddProductToCart(View):
    """Класс динамического добавления товара в корзину по ajax-запросам."""

    @staticmethod
    def get(request):
        user = request.user

        primary_product_shop_id = request.GET.get('primary_product_shop_id')
        amount = request.GET.get('amount')
        shop_product_id = request.GET.get('shop_product_id')

        # Если данные поступили от первого скрипта
        # (добавление товара по главной кнопке)
        if primary_product_shop_id is not None:
            shop_product = ProductOnShopModel.objects.filter(
                id=primary_product_shop_id).select_related(
                'shop', 'product')[0]
            amount = int(amount)
            if amount <= shop_product.quantity:
                quantity = amount
            elif amount == 1:
                return JsonResponse(
                    {'data': {'message_1': 'Товара нет в наличии'}}
                )
            else:
                return JsonResponse(
                    {
                        'data': {
                            'message_1': 'Недостаточно товара.'
                                         ' Попробуйте уменьшить количество.'
                        }
                    }
                )

        # Если данные поступили от второго скрипта
        # (добавление товара через список во вкладке "Продавцы")
        elif shop_product_id is not None:
            shop_product = ProductOnShopModel.objects.filter(
                id=shop_product_id).select_related('shop', 'product')[0]
            if shop_product.quantity > 0:
                quantity = 1
            else:
                return JsonResponse(
                    {'data': {'message_2': 'Товара нет в наличии'}}
                )
        else:
            return JsonResponse({'data': {'error': 'Неверные данные'}})

        # Вычисляем итоговую цену товара
        discount_price = GetDiscountsForProductsService().get_discount_price(
            product=shop_product.product, price=shop_product.price)[0]

        # Проверяем, добавлен ли текущий товар у данного пользователя в корзину
        if not isinstance(user, AnonymousUser):
            # Ищем корзину текущего пользователя
            cart = CartModel.objects.filter(
                user=user, status='actively').prefetch_related('products')

            if not len(cart):  # Если нет корзины - создаем
                cart = CartModel.objects.create(user=user, status='actively')
            else:
                cart = cart[0]

            # Проверяем, если в корзине модель CartProduct с текущим
            # товаром из магазина
            product_in_cart = cart.products.filter(product=shop_product)

            # Если нет - создаем экземпляр класса CartProduct с
            # текущим товаром магазина
            if not len(product_in_cart):
                cart_product = CartProductModel.objects.create(
                    user=user, product=shop_product,
                    quantity=quantity, price=discount_price
                )
                # Добавляем товар в корзину
                AddItemToCart.add_item_to_cart(
                    cart=cart, product=cart_product,
                    amount=quantity, price=discount_price
                )
            else:
                # Если создан, то увеличиваем количество на соответствующее
                # значение и цену модели CartProduct
                cart_product = product_in_cart[0]
                cart_product.quantity += quantity
                cart_product.price = cart_product.quantity * discount_price
                cart_product.save(update_fields=['quantity', 'price'])

                # Увеличиваем количество товара и цену в корзине
                AddItemToCart.increasing_the_number_of_items_in_the_cart(
                    cart=cart, amount=quantity, price=discount_price
                )
            number_of_goods = cart.quantity
        else:
            cart = Cart(request)
            if amount is not None:
                cart.add(
                    product=shop_product, qty=amount, price=discount_price
                )
            else:
                cart.add(product=shop_product, qty=1, price=discount_price)
            number_of_goods = cart.__len__()

        # Передаем количество товара в корзине на страницу

        return JsonResponse({'data': {
            'number_of_goods': number_of_goods,
            'message_1': '',
            'message_2': ''
        }})


class DynamicChangeProductToCart(View):
    """Класс динамического изменения товара в корзине по ajax-запросам."""

    @staticmethod
    def post(request):
        shop_product_id = request.POST.get('shop_product_id')
        action = request.POST.get('action')
        shop_product = ProductOnShopModel.objects.filter(
            id=shop_product_id).first()

        # Изменение количества на 1
        if action == 'add':
            error, count_products_in_cart, total_price_cart = \
                AddItemToCart().change_item_count_cart(
                    request=request, product=shop_product, count=1
                )

        # Изменение количества на -1
        elif action == 'remove':
            error, count_products_in_cart, total_price_cart = \
                AddItemToCart().change_item_count_cart(
                    request=request, product=shop_product, count=-1
                )
        else:
            count_products_in_cart, total_price_cart = 0, 0
        if error is not None:
            return JsonResponse({'error': 'Недостаточно товара'})
        else:
            return JsonResponse({'quantity': count_products_in_cart,
                                 'total_price': total_price_cart})


class CompareView(View):
    """Представление, отображающее страницу сравнения товаров."""
    template_name = 'app_marketplace/compare.html'

    def get(self, request):
        compare_id_list = ComparedProductsListService.get_compared_list(
            request=self.request
        )
        compare_id_list = [value.split() for value in compare_id_list]

        # Список товаров для сравнения и их id в модели Product_on_shop
        # при добавление в список сравнения.
        # id в модели Product_on_shop необходимы для сравнения цен
        compare_list_and_product_on_shop_pk = []

        for product_id, product_on_shop_id in compare_id_list:
            product = ProductModel.objects.filter(
                id=product_id).select_related('category').prefetch_related(
                'characteristics').first()
            if product:
                compare_list_and_product_on_shop_pk.append(
                    (product, product_on_shop_id)
                )

        # Количество сравниваемых товаров должно быть больше единицы
        if len(compare_list_and_product_on_shop_pk) > 1:

            # Проверка, добавлены ли в список сравнения товары одной категории
            products_category = []
            for product, _ in compare_list_and_product_on_shop_pk:
                product_category = product.category.name
                if product_category not in products_category:
                    products_category.append(product_category)

            products_on_shops = []
            for product, product_on_shop_id in \
                    compare_list_and_product_on_shop_pk:
                product_on_shop = ProductOnShopModel.objects.filter(
                    pk=product_on_shop_id).first()
                if product_on_shop:
                    products_on_shops.append((product, product_on_shop))

            # Актуализируем цену сравниваемых товаров с учетом скидок
            compare_list = []
            for product, product_on_shop in products_on_shops:

                if len(GetDiscountsForProductsService.get_discounts(product)):
                    discount_price = \
                        GetDiscountsForProductsService.get_discount_price(
                            product=product, price=product_on_shop.price)[0]
                    compare_list.append(
                        (
                            discount_price,
                            product_on_shop.price,
                            product,
                            product_on_shop.pk
                        )
                    )
                else:
                    compare_list.append(
                        (
                            None,
                            product_on_shop.price,
                            product,
                            product_on_shop.pk
                        )
                    )

            # Если сравниваемые товары принадлежат разной категории
            if len(products_category) > 1:
                statements = [
                    'Товары разные, как мёд и масло...',
                    'Будто сравниваем яблоки и апельсины...',
                ]

                context = {
                    'not_enough_goods': False,
                    'messages': random.choices(statements),
                    'compare_list': compare_list,
                    'incomparable_goods': True
                }
                context['messages'].append(
                    'Сравниваемые товары должны принадлежать одной категории.'
                )
                return render(
                    request=request,
                    template_name=self.template_name,
                    context=context
                )

            product_specifications = {
                product: product.characteristics.all() for
                _, _, product, _ in compare_list
            }

            # Словарь хранения всех характеристик сравниваемых товаров
            all_parameters = dict()

            for product, characteristics in product_specifications.items():
                for characteristic in characteristics:
                    if all_parameters.get(characteristic.name.name, 0):
                        all_parameters.get(characteristic.name.name).update(
                            {product.slug: characteristic.value.value}
                        )
                    else:
                        all_parameters[characteristic.name.name] = {
                            product.slug: characteristic.value.value
                        }

            # Словарь хранения отличаемых характеристик сравниваемых товаров
            different_parameters = dict()
            for key, values in all_parameters.items():
                if len(values.values()) != len(compare_list):
                    different_parameters.update({key: values})
                else:
                    values_lst = list()
                    for value in values.values():
                        values_lst.append(value)
                    if len(set(values_lst)) > 1:
                        different_parameters.update({key: values})

            # Реализация переключателя отображения только отличающихся
            # характеристик товара
            if request.is_ajax() and 'different' in request.GET.keys():

                # Отслеживание состояния переключателя
                different = request.GET.get('different')

                if different == 'true':
                    result = different_parameters
                else:
                    result = all_parameters
                return JsonResponse(
                    {
                        'html': render_to_string(
                            'app_marketplace/diff_param.html',
                            {
                                'characteristics': result,
                                'compare_list': compare_list
                            }
                        )
                    }
                )
            context = {
                'not_enough_goods': False,
                'characteristics': different_parameters,
                'compare_list': compare_list
            }
            return render(
                request=request,
                template_name=self.template_name,
                context=context
            )
        else:
            context = {
                'not_enough_goods': True,
                'compare_list': compare_list_and_product_on_shop_pk
            }
            return render(
                request=request,
                template_name=self.template_name,
                context=context
            )

    def post(self, request):
        if 'del_compare_item' in request.POST.keys():
            product = request.POST['del_compare_item']
            return ComparedProductsListService.delete_item_from_cookies(
                request=request, product=product
            )


class DeliveryInfoView(View):
    pass


class CategoryCatalogView(ListView):
    paginate_by = 8
    model = ProductModel
    template_name = 'app_marketplace/catalog.html'
    ordering = ['view_count']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        products_list, category, shop = CatalogService().get_category_product(
            self.kwargs['slug']
        )
        if products_list:
            price_list = self.request.GET.get('price', None)
            filter_shop = self.request.GET.get('shop', None)
            filter_stock = self.request.GET.get('stock', None)
            filter_manufacturer = self.request.GET.getlist('manufacturer',
                                                           None)
            products_list = CatalogService().filter_product(
                products_list, price_list, filter_shop, filter_stock,
                filter_manufacturer)
            manufacturer_list = [product.manufacturer for product in
                                 products_list]
            manufacturers = set(manufacturer_list)
            manufacturers = sorted(list(manufacturers))
            page = self.request.GET.get('page')
            order = self.request.GET.get('ordering', 'view_count')
            products_list = CatalogService().sort_product(products_list, order)
            products = CatalogService().paginate(
                products_list, self.paginate_by, page
            )
            get_copy = self.request.GET.copy()
            if get_copy.get('page'):
                get_copy.pop('page')
            elif get_copy.get('ordering'):
                get_copy.pop('ordering')
            elif get_copy.get('add_compare_list'):
                get_copy.pop('add_compare_list')
            context['get_copy'] = get_copy
            context['product_paginate'] = products

            if len(products):
                products = [
                    (
                        GetDiscountsForProductsService.get_discount_price(
                            product=product, price=product.min_price)[0] if
                        product.discounts.exists() else product.min_price,
                        product) for product in products
                ]
                min_price = min(product[0] for product in products)
                max_price = max(product[0] for product in products)
                context['products'] = products
                context['min_price'] = int(min_price)
                context['max_price'] = int(max_price)

            price_list = self.request.GET.get('price', None)
            filter_shop = self.request.GET.get('shop', None)

            if price_list:
                prices = price_list.split(';')
                min_filter_price = int(prices[0])
                max_filter_price = int(prices[-1])
                context['min_filter_price'] = min_filter_price
                context['max_filter_price'] = max_filter_price

            context['price_list'] = price_list
            context['filter_shop'] = filter_shop
            context['manufacturers'] = manufacturers
            context['shops'] = shop
            context['category'] = category
            context['orderby'] = order
            return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        product_to_compare = request.GET.get('add_compare_list', None)
        if product_to_compare:
            product = ProductModel.objects.filter(
                product_on_shop__pk=product_to_compare).first()
            if product:
                return ComparedProductsListService.add_item_to_cookies(
                    request=request,
                    product=product,
                    product_on_shop_id=product_to_compare
                )
        destroy = self.request.GET.get('destroy', None)
        if destroy:
            return HttpResponseRedirect(reverse('catalog', kwargs={'slug':self.kwargs['slug']}))
        return self.render_to_response(context)


class ClearCacheAdminView(UserPassesTestMixin, FormView):
    form_class = ClearCacheForm
    template_name = "admin/clearcache.html"

    success_url = reverse_lazy('clearcache_admin')

    def test_func(self):
        # Only super user can clear caches via admin.
        return self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, args, kwargs)
        return response

    def form_valid(self, form):
        try:
            cache_name = form.cleaned_data['cache_name']
            clear_cache(cache_name)
            messages.success(
                self.request, "Кэш успешно очищен '{0}'".format(
                    form.cleaned_data['cache_name']
                )
            )
        except Exception as err:
            messages.error(
                self.request,
                "Не получилось очистить кэш, произошла ошибка: {0}".format(err)
            )
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Очистка кэша'
        return context


class UserOrderView(RegistrationView):
    template_name = "app_marketplace/user_order.html"
    success_url = reverse_lazy('create_order_delivery')

    @classmethod
    def post(cls, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super(UserOrderView, cls).post(request, *args, **kwargs)
        else:
            first_name = request.POST.get('name', None)
            last_name = request.POST.get('last_name', None)
            email = request.POST.get('email', None)

            user = User.objects.get(pk=request.user.id)
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if email:
                user.email = email
            user.save()

            return HttpResponseRedirect(cls.success_url)


class CreateOrderDeliveryView(LoginRequiredMixin, View):
    template_name = 'app_marketplace/create_order_delivery.html'
    success_url = reverse_lazy('create_order_payments')

    @classmethod
    def get(cls, request, **kwargs):
        form = CreateOrderDeliveryForm(request.POST or None)
        order = OrderModel.objects.select_related(
            'cart').filter(
            cart__user=request.user, status='actively'
        ).order_by('date_order').first()
        if order:
            context = {
                'form': form,
                'order': order
            }
        else:
            context = {
                'form': form
            }
        return render(request, cls.template_name, context)

    @classmethod
    def post(cls, request, *args, **kwargs):
        form = CreateOrderDeliveryForm(request.POST or None)
        user_cart = CartModel.objects.get(user=request.user, status='actively')
        order = OrderModel.objects.filter(
            cart=user_cart, status='actively').first()
        if not order:
            order = OrderModel.objects.create(
                cart=user_cart, status='actively')
        if form.is_valid():
            type_delivery = form.cleaned_data['delivery_for_order']

            if (
                    type_delivery.delivery == 'default' and
                    user_cart.total_price > type_delivery.border_free_delivery
            ):
                type_delivery.price = type_delivery.express_price
                order_price = user_cart.total_price + type_delivery.price
            elif type_delivery.delivery == 'online':
                type_delivery.price = type_delivery.express_price
                order_price = user_cart.total_price + type_delivery.price
            else:
                order_price = user_cart.total_price

            order.delivery_for_order = type_delivery
            order.country = form.cleaned_data['country']
            order.street = form.cleaned_data['street']
            order.locality = form.cleaned_data['locality']
            order.house = form.cleaned_data['house']
            order.apartment = form.cleaned_data['apartment']
            order.entrance = form.cleaned_data['entrance']
            order.floor = form.cleaned_data['floor']
            order.order_total_price = order_price
            order.save()
            return HttpResponseRedirect(cls.success_url)
        context = {
            'form': form
        }
        return render(request, cls.template_name, context)


class CreateOrderPaymentView(LoginRequiredMixin, View):
    template_name = 'app_marketplace/create_order_payment.html'
    success_url = reverse_lazy('confirm_order')

    @classmethod
    def get(cls, request, **kwargs):
        form = CreateOrderPaymentForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, cls.template_name, context)

    @classmethod
    def post(cls, request, *args, **kwargs):
        form = CreateOrderPaymentForm(request.POST or None)
        if form.is_valid():
            payment_type = form.cleaned_data['payment_type']
            user_cart = CartModel.objects.get(
                user=request.user, status='actively'
            )
            order = OrderModel.objects.get(cart=user_cart, status='actively')
            order.payment_type = payment_type
            order.save()
            return HttpResponseRedirect(cls.success_url)
        context = {
            'form': form
        }
        return render(request, cls.template_name, context)


class ConfirmOrderView(LoginRequiredMixin, View):
    template_name = 'app_marketplace/confirm_order.html'
    success_url = reverse_lazy('create_payment')

    @classmethod
    def get(cls, request, **kwargs):
        order = OrderModel.objects.select_related(
            'cart',
            'delivery_for_order'
        ).filter(
            cart__user=request.user, status='actively'
        ).order_by('date_order').first()
        product_list = CartProductModel.objects.filter(
            cart=order.cart).select_related('product')
        old_total_cost = sum(
            [product.quantity * product.product.price for
             product in product_list]
        )
        context = {'order': order,
                   'product_list': product_list,
                   'old_total_cost': old_total_cost
                   }
        return render(request, cls.template_name, context)


class CartView(View):
    """Отображение корзины."""
    @classmethod
    def get(cls, request, *args, **kwargs):
        if not isinstance(request.user, AnonymousUser):
            cart = CartModel.objects.filter(
                user=request.user, status='actively').first()
            if cart is not None:
                products_in_cart = AddItemToCart().get_products_list_from_cart(
                    cart=cart)
            else:
                products_in_cart = None
        else:
            products_in_cart = Cart(request)
        context = {'products_in_cart': products_in_cart}
        return render(request, 'app_marketplace/cart.html', context)

    @classmethod
    def post(cls, request, *args, **kwargs):
        if 'productDelete' in request.POST.keys():
            shop_product_id = request.POST['productDelete']
            shop_product = ProductOnShopModel.objects.filter(
                id=shop_product_id).first()

            products_in_cart = AddItemToCart().remove_item_from_cart(
                request=request, product=shop_product
            )

            context = {'products_in_cart': products_in_cart}
            return render(request, 'app_marketplace/cart.html', context)


class DiscountsListView(ListView):
    """
    Представление, отображающее список всех активных скидок,
     которые действуют хотя на один товар.
    """
    paginate_by = 8
    model = DiscountModel
    template_name = 'app_marketplace/discounts.html'
    context_object_name = 'discounts'

    def get_queryset(self):
        today = timezone.now()
        queryset = DiscountModel.objects.filter(
            Q(date_start__date__lte=today) | Q(date_start=None),
            date_end__date__gte=today,
            is_active=True, product__is_active=True
        ).annotate(count_product=Count('product')).order_by('count_product')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DiscountsListView, self).get_context_data()
        discounts = context.get('discounts', None)

        # Словарь для хранения скидки и продукта, который продается с
        # данной скидкой
        data = dict()

        for discount in discounts:
            if not len(data.values()):
                data[discount] = ProductModel.objects.filter(
                    is_active=True, discounts=discount).first()
            else:
                # Уменьшаем количество повторяемых товаров, привязанных к
                # скидкам, чтобы разнообразить изображения скидок
                products = ProductModel.objects.filter(
                    is_active=True, discounts=discount)[:10]
                if len(products) > 1:
                    products_id_in_data = [
                        product.pk for product in data.values()
                    ]
                    for product in products:
                        if product.pk not in products_id_in_data:
                            data[discount] = product
                            break
                    else:
                        data[discount] = products[0]
                elif len(products) == 1:
                    data[discount] = products[0]
        context['discounts'] = data
        context['title'] = 'О скидках'
        context['home'] = 'Главная'
        context['blog'] = 'О скидках'
        return context


class DiscountDetailView(DetailView):
    """Представление, отображающее детальную информацию о скидке."""
    model = DiscountModel
    template_name = 'app_marketplace/discount_detail.html'
    slug_url_kwarg = 'discount_slug'
    context_object_name = 'discount'

    def get_queryset(self):
        discount_slug = self.kwargs['discount_slug']
        today = timezone.now()
        queryset = DiscountModel.objects.filter(
            Q(date_start__date__lte=today) | Q(date_start=None),
            date_end__date__gte=today,
            slug=discount_slug,
            is_active=True
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DiscountDetailView, self).get_context_data()
        discount = context.get('discount')
        product = ProductModel.objects.filter(
            is_active=True, discounts=discount).first()
        context['product'] = product
        context['title'] = discount.name
        context['home'] = 'Главная'
        context['blog'] = 'Все о скидке'
        return context


class CreatePayment(FormView):
    form_class = CreatePaymentForm
    template_name = 'app_marketplace/create_payment.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(CreatePayment, self).get_context_data()
        user_cart = CartModel.objects.filter(
            user=self.request.user, status='actively'
        )
        order = OrderModel.objects.get(cart=user_cart[0], status='actively')
        context['order'] = order
        return context

    def form_valid(self, form):
        card_number = form.cleaned_data['card_number']
        user_cart = CartModel.objects.filter(
            user=self.request.user, status='actively'
        )
        order = OrderModel.objects.get(cart=user_cart[0], status='actively')
        PaymentService.order_payment(
            order=order, price=order.order_total_price, card_number=card_number
        )
        return super().form_valid(form)


class SearchProductsView(generic.ListView):
    model = ProductModel
    template_name = 'app_marketplace/search_products.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = ProductModel.objects.filter(
            Q(model__icontains=query) | Q(description__icontains=query)
        )
        return object_list


class CategoryListView(ListView):
    model = CategoryModel
    template_name = 'app_marketplace/categories.html'
    context_object_name = 'categories'


class ShopListView(ListView):
    model = ShopModel
    template_name = 'app_marketplace/shop-list.html'
    context_object_name = 'shop_list'
