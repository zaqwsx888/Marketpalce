from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Min, Count, Max, IntegerField
from django.http import HttpResponseRedirect
from django.utils import timezone
from .cart import Cart
from .models import (
    ReviewModel, ProductViewHistoryModel, ProductModel, OrderModel,
    PurchaseHistoryModel, CategoryModel, ShopModel, CartModel,
    ProductOnShopModel
)
from .serializers import PaymentSerializer
from .tasks import payment_request


class GetAdminSettingsService:
    """Получение административных настроек."""
    pass


class AddLookedProductsService:
    """
    Сервис добавления товара в список просмотренных товаров
     пользователем.
    """
    @classmethod
    def add_item_to_watch_list(cls, user, product):
        """
        Добавление товара в список просмотренных товаров. Если список включает
         более 20 товаров у текущего пользователя, товары добавленные ранее
          будут удалены из базы.
        """
        if not cls.is_product_already_in_watch_list(user, product):
            ProductViewHistoryModel.objects.create(user=user, product=product)
        ProductViewHistoryModel.objects.filter(
            user=user,
            pk__in=ProductViewHistoryModel.objects.order_by(
                'pk').values_list('pk')[20:]
        ).delete()

    @classmethod
    def remove_item_from_watch_list(cls, user, product):
        """Метод удаления товара из списка просмотренных товаров."""
        product = ProductViewHistoryModel.objects.filter(
            user=user, product=product
        )
        product.delete()

    @classmethod
    def get_a_list_of_viewed_products(cls, user, quantity=None):
        """
        Метод получения списка просмотренных товаров пользователем
         в заданном количестве.
        """
        if quantity:
            if 1 <= quantity <= 19:
                user_view_history = ProductViewHistoryModel.objects.filter(
                    user=user).select_related('product')[:quantity]
            else:
                user_view_history = ProductViewHistoryModel.objects.filter(
                    user=user).select_related('product')[:3]
        else:
            user_view_history = ProductViewHistoryModel.objects.filter(
                user=user).select_related('product')
        return user_view_history

    @classmethod
    def is_product_already_in_watch_list(cls, user, product):
        """
        Метод, информирующий есть ли переданный товар в списке просмотренных
         товаров. При наличии товара возвращается True, иначе False.
        """
        product = ProductViewHistoryModel.objects.filter(
            user=user, product=product
        )
        if len(product):
            return True
        return False

    @classmethod
    def get_the_number_of_items_viewed(cls, user):
        """
        Метод, передающий количество товаров в истории просмотров у
         текущего пользователя.
        """
        quantity = ProductViewHistoryModel.objects.filter(user=user).count()
        return quantity


class GetPurchaseHistoryService:
    """Сервис получения истории заказов и покупок пользователем."""
    @classmethod
    def get_orders_history(cls, user):
        user_orders_history = OrderModel.objects.prefetch_related(
            'payment_for_order', 'delivery_for_order'
        ).filter(cart__user=user).order_by('-date_order')
        return user_orders_history

    @classmethod
    def get_purchase_history(cls, user):
        user_purchase_history = PurchaseHistoryModel.objects.filter(
            order__cart__user=user).order_by('-date_purchase')
        return user_purchase_history


class GetDiscountsForProductsService:
    """Сервис получения скидок на товары."""
    @classmethod
    def get_discounts(cls, product: ProductModel) -> list:
        """
        Получение всех действующих скидок на товар. Метод получает экземпляры
         класса товара, после чего осуществляется обращение в базу данных для
          получения всех действующих скидок.
        """
        today = timezone.now()
        discounts = product.discounts.filter(
            Q(date_start__date__lte=today) | Q(date_start=None),
            is_active=True, date_end__date__gte=today
        ).select_related('type_of_discount').filter(
            type_of_discount__is_active=True)
        return list(discounts)

    @classmethod
    def get_priority_discount(cls, product: ProductModel):
        """
        Получение приоритетных скидок на товары. Метод получает экземпляры
         класса товаров в виде множества (чтобы предотвратить повторы),
          после чего обращается по каждому товару в базу данных чтобы получить
           все действующие скидки с наибольшим весом на текущий товар.
        """
        today = timezone.now()
        discount = product.discounts.filter(
            Q(date_start__date__lte=today) | Q(date_start=None),
            is_active=True, date_end__date__gte=today
        ).select_related('type_of_discount').filter(
            type_of_discount__is_active=True).order_by(
            '-type_of_discount__weight').first()
        return discount

    @classmethod
    def get_discount_price(cls, product: ProductModel, price) -> tuple:
        """
        Метод расчета цены товара с учетом действующей наиболее приоритетной
         скидки. Максимальная скидка составляет 99 % от цены товара.
        """
        discount = cls.get_priority_discount(product)
        if discount:
            discount_prices = 0
            percent_discount = discount.percent_discount
            value_discount = discount.value_discount
            if percent_discount:
                percent_discount = percent_discount
                new_price = price - price * percent_discount / 100
                if new_price >= price * 1 / 100:
                    discount_prices = new_price
                else:
                    discount_prices = price * 1 / 100
            elif value_discount:
                value_discount = value_discount
                new_price = price - value_discount
                if new_price >= price * 1 / 100:
                    discount_prices = new_price
                else:
                    discount_prices = price * 1 / 100
            price = round(discount_prices, 2)
        return price, discount


class AddItemToCart:
    """Сервис добавления товара в корзину."""
    @classmethod
    def add_item_to_cart(cls, cart, product, amount, price):
        """Добавление товара в корзину."""
        cart.quantity += amount
        cart.total_price += price * amount
        cart.products.add(product)
        cart.save()

    @classmethod
    def increasing_the_number_of_items_in_the_cart(cls, cart, amount, price):
        """Увеличение количества товара в корзине."""
        cart.quantity += amount
        cart.total_price += price * amount
        cart.save()

    @classmethod
    def remove_item_from_cart(cls, request, product):
        """Убирает товар из корзины."""
        if not isinstance(request.user, AnonymousUser):
            cart = CartModel.objects.filter(
                user=request.user, status='actively').prefetch_related(
                'products').first()
            cart_product = cart.products.get(product=product)

            cart.total_price -= cart_product.price * cart_product.quantity
            if cart.total_price < 0:
                cart.total_price = 0

            cart.quantity -= cart_product.quantity
            if cart.quantity < 0:
                cart.quantity = 0

            cart.products.remove(cart_product)
            cart.save()
            cart_product.delete()

            new_cart = CartModel.objects.filter(
                user=request.user, status='actively').prefetch_related(
                'products').first()
            products_in_cart = AddItemToCart().get_products_list_from_cart(
                cart=new_cart
            )
        else:
            cart = Cart(request)
            cart.delete(product)
            products_in_cart = cart

        return products_in_cart

    @classmethod
    def change_item_count_cart(cls, request, product, count):
        """Изменяет количество товара в CartProduct."""
        if not isinstance(request.user, AnonymousUser):
            cart = CartModel.objects.filter(
                user=request.user, status='actively').prefetch_related(
                'products').first()

            cart_product = cart.products.get(product=product)
            if count < 0:
                cart_product.price -= product.price
                cart.total_price -= product.price
            else:
                if product.quantity >= count:
                    cart_product.price += product.price
                    cart.total_price += product.price
                else:
                    return 'error', None, None

            cart_product.quantity += count
            cart.quantity += count
            product.quantity -= count

            cart_product.save()
            product.save()
            cart.save()
            count_products_in_cart = cart.quantity
            total_price_cart = cart.total_price

        else:
            if product.quantity >= count:
                product.quantity -= count
                product.save()
                cart = Cart(request)
                cart.update(product, qty=count)
                count_products_in_cart = cart.__len__()
                total_price_cart = cart.get_total_price()
            else:
                return 'error', None, None

        return None, count_products_in_cart, total_price_cart

    @classmethod
    def get_products_list_from_cart(cls, cart):
        """Возвращает список товаров в корзине."""
        products_list = list(cart.products.all())
        return products_list

    @classmethod
    def get_products_count(cls, cart):
        """Возвращает количество товаров в корзине."""
        return cart.quantity

    @classmethod
    def get_cart_prices(cls, cart):
        """Возвращает стоимость корзины."""
        return cart.total_price


class AddCommentToProductService:
    """Добавление отзыва к товару."""
    @classmethod
    def add_feedback(cls, product, user, text=None):
        """Добавление отзыва к товару."""
        review = ReviewModel.objects.create(product=product, user=user)
        if text is not None:
            review.review = text
            review.save(update_fields=['review'])
        else:
            review.review = text
            review.save(update_fields=['review'])

    @classmethod
    def get_review_list(cls, product, is_active=True, count=None):
        reviews = product.review.filter(is_active=is_active)
        if count is None:
            return list(reviews)
        else:
            return list(reviews[:count])

    @classmethod
    def get_discount_to_cart(cls, cart):
        pass

    @classmethod
    def get_review_count(cls, product):
        reviews = product.review.filter(is_active=True).count()
        return reviews


class ComparedProductsListService:
    """Список сравниваемых товаров."""
    @classmethod
    def add_item_to_cookies(cls, request, product, product_on_shop_id):
        response = HttpResponseRedirect(request.path)
        qnt_comparison = cls.get_compared_list(request)
        if len(qnt_comparison) < 4:
            response.set_cookie(
                key=f'compare_{product.slug}',
                value=f'{product.id} {product_on_shop_id}'
            )
            print(response)
        return response

    @classmethod
    def delete_item_from_cookies(cls, request, product):
        response = HttpResponseRedirect(request.path)
        response.delete_cookie(f'compare_{product}')
        return response

    @classmethod
    def get_compared_list(cls, request):
        cookies = request.COOKIES
        out = [cookies[product] for product in cookies
               if product.startswith('compare_')]
        return out


class PaymentService:
    """Сервис оплаты."""
    @classmethod
    def order_payment(cls, order, price, card_number):
        """Оплатить заказ."""
        serializer = PaymentSerializer(
            data={
                'order_number': order.pk,
                'bank_card': card_number.replace(' ', ''),
                'price': price
            }
        )
        if serializer.is_valid():
            payment_request.delay(serializer.data)

    @classmethod
    def get_order_payment_status(cls):
        """Получить статус оплаты заказа."""
        pass


class HomePageService:
    """
    Сервис для реализации блоков "Предложения дня", "Популярные товары",
     "Горячие предложения", "Ограниченный тираж" на главной странице.
    """
    @classmethod
    def get_random_product(cls):
        """Получение случайного товара из ограниченного тиража."""
        products = ProductOnShopModel.objects.select_related('product').filter(
            product__is_active=True)
        limited_deals = ProductModel.objects.select_related().annotate(
                min_price=Min(
                    'product_on_shop__price', output_field=IntegerField()
                )
            ).filter(
            limited_edition=True, product_on_shop__in=products
        ).order_by('?').first()
        return limited_deals

    @classmethod
    def get_top_products(cls):
        """Метод получения популярных товаров."""
        top_products = {}
        products = ProductModel.objects.filter(is_active=True).select_related(
            'category', 'main_image').order_by('-view_count')[:20]
        for product in products:
            product_on_shop = ProductOnShopModel.objects.filter(
                product=product, for_sale=True).order_by('price').first()
            top_products.update({product: product_on_shop})
        return top_products

    @classmethod
    def get_hot_offers(cls):
        """
        Метод получения товаров для блока "Горячие предложения" - до 9 товаров,
         на которых действует какая-нибудь акция.
        """
        hot_offers = {}
        products = ProductModel.objects.filter(
            is_active=True).exclude(discounts=None).order_by('?')[:20]
        products = [
            product for product in products
            if GetDiscountsForProductsService.get_priority_discount(product)
        ]
        for product in products:
            if len(hot_offers) < 10:
                product_on_shop = ProductOnShopModel.objects.filter(
                    product=product, for_sale=True, quantity__gte=1
                ).order_by('price').first()
                if product_on_shop:
                    hot_offers.update({product: product_on_shop})
            else:
                break
        return hot_offers

    @classmethod
    def get_limited_products(cls, offer_of_day):
        """
        Получение списка 16 товаров ограниченного тиража,
        за исключением товара из отдельного блока Limited Deals.
        """
        limited_products = {}
        products = ProductModel.objects.filter(
            is_active=True, limited_edition=True).exclude(
            id=offer_of_day.id).select_related('category', 'main_image')[:20]
        for product in products:
            if len(limited_products) < 17:
                product_on_shop = ProductOnShopModel.objects.filter(
                    product=product, for_sale=True, quantity__gte=1
                ).order_by('price').first()
                if product_on_shop:
                    limited_products.update({product: product_on_shop})
            else:
                break
        return limited_products


class CatalogService:
    """Блок каталога."""
    @classmethod
    def get_category_product(cls, slug):

        products = ProductOnShopModel.objects.select_related('product').filter(
            product__is_active=True)

        products = ProductModel.objects.select_related().annotate(
            min_price=Min(
                'product_on_shop__price', output_field=IntegerField()
            ),
            max_price=Max(
                'product_on_shop__price', output_field=IntegerField()
            ),
            num_reviews=Count('review')).filter(
            category__slug=slug, product_on_shop__in=products
        )
        category = CategoryModel.objects.get(slug=slug)
        shop = ShopModel.objects.filter(
            product_on_shop__product__category__slug=slug
        ).distinct()
        return products, category, shop

    @classmethod
    def filter_product(cls, queryset, price_list, shop,
                       delivery, manufacturer):
        if price_list:
            price_list = price_list.split(';')
            min_price = price_list[0]
            max_price = price_list[1]
            queryset = queryset.filter(
                min_price__gte=min_price, min_price__lte=max_price
            )
        if shop:
            queryset = queryset.filter(product_on_shop__shop__name=shop)
        if manufacturer:
            queryset = queryset.filter(manufacturer__in=manufacturer)

        if delivery:
            queryset = queryset.filter(product_on_shop__quantity__gt=0)

        return queryset

    @classmethod
    def sort_product(cls, queryset, order):
        sorted_products = queryset.order_by(order)
        return sorted_products

    @classmethod
    def paginate(cls, product_list, paginate_by, page=1):
        paginator = Paginator(product_list, paginate_by)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        return products
