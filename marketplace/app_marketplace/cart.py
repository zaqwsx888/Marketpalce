from decimal import Decimal
from app_marketplace.models import ProductOnShopModel
from django.conf import settings
import copy


class Cart:
    """Инициализируем корзину."""
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        product_ids = self.cart.keys()
        products = ProductOnShopModel.objects.filter(id__in=product_ids)
        cart = copy.deepcopy(self.cart)

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price']) * item['qty']
            item['quantity'] = item['qty']
            yield item

    def __len__(self):
        """Количество товара в корзине."""
        return sum(item['qty'] for item in self.cart.values())

    def add(self, product, qty, price=None):
        """Добавление и обновление товара в корзине сессии."""
        product_id = str(product.id)

        if product_id in self.cart:
            self.cart[product_id]['qty'] = self.cart[product_id]['qty'] + qty
        else:
            self.cart[product_id] = {'price': str(price), 'qty': qty}

        self.save()

    def update(self, product, qty):
        """Обновление количества товара."""
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['qty'] = self.cart[product_id]['qty'] + qty
        self.save()

    def delete(self, product):
        """Удаление товара."""
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self):
        """Сумма товаров в корзине."""
        return sum(
            Decimal(item['price']) * item['qty'] for item in self.cart.values()
        )

    def save(self):
        """Сохранение сессии."""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        """Очищаем корзину в сессии."""
        del self.session[settings.CART_SESSION_ID]
        self.save()
