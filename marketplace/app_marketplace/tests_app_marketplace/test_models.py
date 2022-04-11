from app_marketplace.models import CategoryModel, CharacteristicModel, \
    CharacteristicNameModel, ValueModel, ShopAddressModel, ShopModel, \
    TypeOfDiscountModel, DiscountModel, ProductModel, FilesModel, TagsModel, \
    ProductOnShopModel, ProductGroupModel, ReviewModel, CartProductModel, \
    CartModel, OrderModel, ProductViewHistoryModel, PurchaseHistoryModel, \
    DeliveryModel, PaymentModel, StatusModel, BannerModel
from django.test import TestCase


class TestModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.models = {CategoryModel: {
            'verbose_name': 'Категория',
            'verbose_name_plural': 'Категории'},
            CharacteristicModel: {
                'verbose_name': 'Характеристика',
                'verbose_name_plural': 'Характеристики'},
            CharacteristicNameModel: {
                'verbose_name': 'Название характеристики',
                'verbose_name_plural': 'Названия характеристик'},
            ValueModel: {
                'verbose_name': 'Значение характеристикик',
                'verbose_name_plural': 'Значения характеристик'},
            ShopAddressModel: {
                'verbose_name': 'Адрес',
                'verbose_name_plural': 'Адреса'},
            ShopModel: {
                'verbose_name': 'Магазин',
                'verbose_name_plural': 'Магазины'},
            TypeOfDiscountModel: {
                'verbose_name': 'Тип скидки',
                'verbose_name_plural': 'Типы скидок'},
            DiscountModel: {
                'verbose_name': 'Скидка',
                'verbose_name_plural': 'Скидки'},
            ProductModel: {
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары'},
            FilesModel: {
                'verbose_name': 'Файл',
                'verbose_name_plural': 'Файлы'},
            TagsModel: {
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги'},
            ProductOnShopModel: {
                'verbose_name': 'Товар магазина',
                'verbose_name_plural': 'Товары магазина'},
            ProductGroupModel: {
                'verbose_name': 'Группа товаров',
                'verbose_name_plural': 'Группы товаров'},
            ReviewModel: {
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы'},
            CartProductModel: {
                'verbose_name': 'Товар в корзине',
                'verbose_name_plural': 'Товары в корзине'},
            CartModel: {
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзины'},
            OrderModel: {
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы'},
            ProductViewHistoryModel: {
                'verbose_name': 'История просмотра',
                'verbose_name_plural': 'Истории просмотров'},
            PurchaseHistoryModel: {
                'verbose_name': 'История покупок',
                'verbose_name_plural': 'Истории покупок'},
            DeliveryModel: {
                'verbose_name': 'Доставка',
                'verbose_name_plural': 'Доставки'},
            PaymentModel: {
                'verbose_name': 'Оплата',
                'verbose_name_plural': 'Оплата'},
            StatusModel: {
                'verbose_name': 'Статус',
                'verbose_name_plural': 'Статусы'},
            BannerModel: {
                'verbose_name': 'Баннер',
                'verbose_name_plural': 'Баннеры'}}

    def test_verbose_name(self):
        for model, value in self.models.items():
            self.assertEqual(model._meta.verbose_name,
                             value['verbose_name'])
            self.assertEqual(model._meta.verbose_name_plural,
                             value['verbose_name_plural'])
