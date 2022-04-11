from http import HTTPStatus
from datetime import datetime, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse, resolve
from app_marketplace import views
from django.views.generic import TemplateView
from app_users.models import User
from app_marketplace.models import FilesModel, ShopAddressModel, ShopModel, \
    CategoryModel, ProductModel, ProductOnShopModel, CartModel, OrderModel, \
    DiscountModel, TypeOfDiscountModel, CartProductModel


class TestUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin')
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
        cls.address_shop = ShopAddressModel.objects.create(
            country='Russia',
            city='unknown',
            street='unknown',
            house='1')
        cls.shop = ShopModel.objects.create(
            name='sitilink',
            description='sitilink',
            phone='3435',
            email='sitilink@mail.ru',
            slug='sitilink',
            image=cls.file)
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
        cls.product_on_shop = ProductOnShopModel.objects.create(
            shop=cls.shop,
            product=cls.product,
            quantity=1,
            price=10.0,
            for_sale=True)
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
            slug="discount")
        cls.cart_product = CartProductModel.objects.create(
            product=cls.product_on_shop,
            user=cls.user,
            quantity=1,
            price=10.0)
        cls.cart = CartModel.objects.create(
            user=cls.user,
            quantity=1,
            total_price=10.0,
            status='actively')

        cls.cart.products.add(cls.cart_product)
        cls.order = OrderModel.objects.create(
            cart=cls.cart,
            payment_type='online',
            status='actively',
            order_total_price=10.0)

        cls.public_urls = (
            (reverse('main'), views.MainPageView, 'app_marketplace/home.html'),
            (reverse('shop_list'), views.ShopListView,
             'app_marketplace/shop-list.html'),
            (reverse('shop', args=['sitilink']), views.ShopDetailView,
             'app_marketplace/shop_details.html'),
            (reverse('category_list'), views.CategoryListView,
             'app_marketplace/categories.html'),
            (reverse('catalog', args=['telefons']), views.CategoryCatalogView,
             'app_marketplace/catalog.html'),
            (reverse('user_order'), views.UserOrderView,
             "app_marketplace/user_order.html"),
            (reverse('create_order_delivery'), views.CreateOrderDeliveryView,
             'app_marketplace/create_order_delivery.html'),
            (reverse('create_order_payments'), views.CreateOrderPaymentView,
             'app_marketplace/create_order_payment.html'),
            (reverse('confirm_order'), views.ConfirmOrderView,
             'app_marketplace/confirm_order.html'),
            (reverse('delivery'), views.DeliveryInfoView, None),
            (reverse('create_payment'), views.CreatePayment,
             'app_marketplace/create_payment.html'),
            (reverse('good_details', args=['telefon']),
             views.ProductDetailView,
             'app_marketplace/product_details.html'),
            (reverse('compare'), views.CompareView,
             'app_marketplace/compare.html'),
            (reverse('cart'), views.CartView, 'app_marketplace/cart.html'),
            (reverse('discounts'), views.DiscountsListView,
             'app_marketplace/discounts.html'),
            (reverse('discount_detail', args=['discount']),
             views.DiscountDetailView, 'app_marketplace/discount_detail.html'),
            (reverse('add_cart_product'), views.DynamicAddProductToCart, None),
            (reverse('change_cart_product'), views.DynamicChangeProductToCart,
             None),
            (reverse('search_products'), views.SearchProductsView,
             'app_marketplace/search_products.html'),
            (reverse('contact'), TemplateView, None),)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_url_is_resolved(self):
        for url, view, template in self.public_urls:
            if template is not None:
                if 'order' in url:
                    c = self.auth_client
                else:
                    c = self.guest_client
                if 'search_products' in url:
                    response = c.get(url, data={'q': 'tele'})
                else:
                    response = c.get(url)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEquals(resolve(url).func.view_class, view)
