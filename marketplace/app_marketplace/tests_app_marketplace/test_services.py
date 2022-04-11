from django.test import TestCase, Client
import app_marketplace.services as serv
from app_marketplace.models import ProductModel, FilesModel, CategoryModel, \
    ProductOnShopModel, ShopModel, ProductViewHistoryModel, CartModel, \
    OrderModel, CartProductModel, PurchaseHistoryModel, TypeOfDiscountModel, \
    DiscountModel
from django.core.files.uploadedfile import SimpleUploadedFile
from app_users.models import User
from datetime import datetime, timedelta
from decimal import Decimal


class BaseConf(TestCase):
    @classmethod
    def setUpClass(cls) -> object:
        super().setUpClass()
        cls.user = User.objects.create_user(username='user12')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        image_name = 'small.jpg'

        uploaded = SimpleUploadedFile(
            name=image_name,
            content=small_gif,
            content_type='image/jpg'
        )

        cls.file = FilesModel.objects.create(file=uploaded)
        cls.type_disc = TypeOfDiscountModel.objects.create(
            name="discount",
            description="discount",
            is_active=True,
            weight=1)
        now_2 = datetime.now() + timedelta(days=10)
        cls.discount = DiscountModel.objects.create(
            name="discount",
            description="discount",
            type_of_discount=cls.type_disc,
            date_end=now_2.isoformat(timespec='seconds') + 'Z',
            is_active=True,
            slug="discount",
            percent_discount=Decimal(5))
        cls.category = CategoryModel.objects.create(
            name='telefons',
            slug='telefons',
            icon=cls.file)
        cls.product = ProductModel.objects.create(
            model='telefon',
            description='telefon',
            category=cls.category,
            main_image=cls.file,
            slug='telefon',
            is_active=True)
        cls.product.discounts.add(cls.discount)
        cls.shop = ShopModel.objects.create(
            name='sitilink',
            description='sitilink',
            phone='3435',
            email='sitilink@mail.ru',
            slug='sitilink',
            image=cls.file)
        cls.product_on_shop = ProductOnShopModel.objects.create(
            shop=cls.shop,
            product=cls.product,
            quantity=1,
            price=Decimal(10.0),
            for_sale=True)
        cls.cart_product = CartProductModel.objects.create(
            product=cls.product_on_shop,
            user=cls.user,
            quantity=1,
            price=Decimal(10.0))
        cls.cart = CartModel.objects.create(
            user=cls.user,
            quantity=1,
            total_price=Decimal(10.0),
            status='actively')
        cls.cart.products.add(cls.cart_product)
        cls.order = OrderModel.objects.create(
            cart=cls.cart,
            payment_type='online',
            status='actively',
            order_total_price=10.0)


class TestLookedProduct(BaseConf):
    @classmethod
    def setUpClass(cls) -> object:
        super().setUpClass()
        cls.serv_locked = serv.AddLookedProductsService()

    def test_watch_list(self):
        self.serv_locked.add_item_to_watch_list(self.user, self.product)
        res = ProductViewHistoryModel.objects.filter(user=self.user).first()
        self.assertEqual(res.product, self.product)

        res_v2 = self.serv_locked.get_a_list_of_viewed_products(self.user, 1)
        self.assertEqual(res, res_v2.first())

        res_v3 = self.serv_locked.is_product_already_in_watch_list(
            self.user, self.product)
        self.assertTrue(res_v3)

        quantity = self.serv_locked.get_the_number_of_items_viewed(self.user)
        self.assertEqual(quantity, 1)

        self.serv_locked.remove_item_from_watch_list(self.user, self.product)
        res_v4 = ProductViewHistoryModel.objects.filter(user=self.user).first()
        self.assertEqual(res_v4, None)


class TestPurchaseHistory(BaseConf):
    @classmethod
    def setUpClass(cls) -> object:
        super().setUpClass()
        cls.serv_purchase_history = serv.GetPurchaseHistoryService()

    def test_history_order(self):
        order_history = self.serv_purchase_history.get_orders_history(
            self.user)
        self.assertEqual(order_history.first(), self.order)

    def test_history_purchase(self):
        self.purchase_history = PurchaseHistoryModel.objects.create(
            order=self.order)
        purchase_history = self.serv_purchase_history.get_purchase_history(
            self.user)
        self.assertEqual(purchase_history.first(), self.purchase_history)


class TestGetDiscount(BaseConf):
    @classmethod
    def setUpClass(cls) -> object:
        super().setUpClass()
        cls.serv_discounts = serv.GetDiscountsForProductsService()

    def test_get_discounts(self):
        discounts = self.serv_discounts.get_discounts(self.product)
        self.assertEqual(discounts[0], self.discount)

    def test_get_priority_discount(self):
        discount = self.serv_discounts.get_priority_discount(self.product)
        self.assertEqual(discount, self.discount)

    def test_get_discount_price(self):
        price, discount = self.serv_discounts.get_discount_price(
            self.product, self.product_on_shop.price)
        self.assertEqual(self.discount, discount)
        new_price = \
            self.product_on_shop.price - \
            self.product_on_shop.price * self.discount.percent_discount / 100
        self.assertEqual(new_price, price)


class TestAddItemToCart(BaseConf):
    @classmethod
    def setUpClass(cls) -> object:
        super().setUpClass()
        cls.serv_cart = serv.AddItemToCart()

    def setUp(self) -> None:
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_remove_item_from_cart(self):
        products = self.serv_cart.remove_item_from_cart(
            self.auth_client.request().wsgi_request, self.product_on_shop)
        self.assertEqual(len(products), 0)

    def test_add_item_and_update_quantity(self):
        cart_product = CartProductModel.objects.create(
            user=self.user, product=self.product_on_shop,
            quantity=self.product_on_shop.quantity,
            price=self.product_on_shop.price
        )
        cart = CartModel.objects.create(user=self.user, status='actively')
        self.serv_cart.add_item_to_cart(cart, cart_product,
                                        cart_product.quantity,
                                        cart_product.price)
        self.assertEqual(cart.products.first(), cart_product)
        self.assertEqual(cart.products.first().quantity,
                         cart_product.quantity)

        self.serv_cart.increasing_the_number_of_items_in_the_cart(
            cart, cart_product.quantity, cart_product.price)
        self.assertEqual(cart.quantity, cart_product.quantity + 1)

    def test_change_item_count_cart(self):
        error, count_products_in_cart, total_price_cart = \
            self.serv_cart.change_item_count_cart(
                self.auth_client.request().wsgi_request, self.product_on_shop,
                1)
        self.assertEqual(count_products_in_cart, 2)
        self.assertEqual(total_price_cart,
                         Decimal(self.product_on_shop.price) * 2)

    def test_get_products_list_from_cart(self):
        resp = self.serv_cart.get_products_list_from_cart(self.cart)
        self.assertEqual(resp, list(self.cart.products.all()))

    def test_get_products_count(self):
        resp = self.serv_cart.get_products_count(self.cart)
        self.assertEqual(resp, self.cart.quantity)

    def test_get_cart_prices(self):
        resp = self.serv_cart.get_cart_prices(self.cart)
        self.assertEqual(resp, self.cart.total_price)


class TestReview(BaseConf):
    @classmethod
    def setUpClass(cls) -> object:
        super().setUpClass()
        cls.serv_review = serv.AddCommentToProductService()

    def setUp(self) -> None:
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_review(self):
        self.serv_review.add_feedback(self.product, self.user, 'Норм')
        reviews = self.serv_review.get_review_list(self.product)
        self.assertEqual(reviews[0].review, 'Норм')
        count = self.serv_review.get_review_count(self.product)
        self.assertEqual(count, 1)


class TestCatalogService(BaseConf):
    @classmethod
    def setUpClass(cls) -> object:
        super().setUpClass()
        cls.serv_catalog = serv.CatalogService()

    def test_get_category_product(self):
        products, category, shop = self.serv_catalog.get_category_product(
            'telefons')
        self.assertEqual(products.first(), self.product)
        self.assertEqual(category, self.category)
        self.assertEqual(shop.first(), self.shop)
