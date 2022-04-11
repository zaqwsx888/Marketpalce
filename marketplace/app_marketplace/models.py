import os
from binascii import hexlify
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .utils import validate_size_file

User = get_user_model()


def _createHash():
    """This function generate 10 character long hash"""
    return hexlify(os.urandom(5))


class CategoryModel(models.Model):
    """Модель категорий."""
    icon = models.ForeignKey('FilesModel', verbose_name=_('Иконка категории'),
                             related_name='category',
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    slug = models.SlugField(max_length=255, unique=True, db_index=True,
                            verbose_name='URL (slag)')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ['id']


class CharacteristicModel(models.Model):
    """Характеристика продукта."""
    name = models.ForeignKey(
        'CharacteristicNameModel', on_delete=models.CASCADE,
        verbose_name=_('Название')
    )
    value = models.ForeignKey(
        'ValueModel', on_delete=models.CASCADE,
        verbose_name=_('Значение')
    )

    def __str__(self):
        return f'{self.name}: {self.value}'

    class Meta:
        verbose_name = _('Характеристика')
        verbose_name_plural = _('Характеристики')
        ordering = ['id']


class CharacteristicNameModel(models.Model):
    """Название характеристики продукта."""
    name = models.CharField(max_length=255,
                            verbose_name=_('Название'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Название характеристики')
        verbose_name_plural = _('Названия характеристик')
        ordering = ['id']


class ValueModel(models.Model):
    """Значения характеристик."""
    value = models.CharField(max_length=255,
                             verbose_name=_('Значение'))

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = _('Значение характеристикик')
        verbose_name_plural = _('Значения характеристик')
        ordering = ['id']


class ShopAddressModel(models.Model):
    """Адрес магазина."""
    country = models.CharField(max_length=255, verbose_name=_('Страна'),
                               blank=True)
    city = models.CharField(max_length=255, verbose_name=_('Город'))
    street = models.CharField(max_length=255, verbose_name=_('Улица'))
    house = models.CharField(max_length=255, verbose_name=_('Дом'))
    floor = models.CharField(max_length=255, verbose_name=_('Этаж'),
                             blank=True)

    class Meta:
        verbose_name = _('Адрес')
        verbose_name_plural = _('Адреса')
        ordering = ['id']

    def __str__(self):
        return f'{self.city}, {_("ул.")} {self.street}, {_("д.")} {self.house}'


class ShopModel(models.Model):
    """Модель магазина."""
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'))
    image = models.ForeignKey(
        'FilesModel', on_delete=models.CASCADE, related_name='shop_image',
        verbose_name=_('Изображение'), blank=True, )
    phone = models.CharField(max_length=25, unique=True,
                             verbose_name=_('Телефон'))
    email = models.EmailField(db_index=True, verbose_name='email',
                              unique=True, max_length=60)
    slug = models.SlugField(max_length=255, unique=True, db_index=True,
                            verbose_name='URL (slag)')
    address = models.ManyToManyField(ShopAddressModel, related_name='shop',
                                     verbose_name=_('Адрес'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = _('Магазин')
        verbose_name_plural = _('Магазины')
        ordering = ['id']


@receiver(post_save, sender=ShopModel)
def tags_clear_cache_shop_model(sender, instance, **kwargs):
    """Функция очистки кэша по сигналу при изменении модели ShopModel."""
    shop_cache_key = 'shop:{}'.format(instance.slug)
    if cache.get(shop_cache_key) is not None:
        cache.delete(shop_cache_key)


class TypeOfDiscountModel(models.Model):
    """Типы скидок.
    """
    name = models.CharField(max_length=255, verbose_name=_('Тип скидки'))
    description = models.TextField(max_length=255,
                                   verbose_name=_('Скидка'))
    weight = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_('Вес скидки'))
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Тип скидки')
        verbose_name_plural = _('Типы скидок')
        ordering = ['id']

    def __str__(self):
        return self.name


class DiscountModel(models.Model):
    """Скидка на товар."""
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    description = models.TextField(max_length=255,
                                   verbose_name=_('Описание'))
    type_of_discount = models.ForeignKey(
        TypeOfDiscountModel, on_delete=models.CASCADE,
        verbose_name=_('Тип скидки')
    )
    date_start = models.DateTimeField(
        verbose_name=_('Дата начала'), blank=True, null=True, validators=[]
    )
    date_end = models.DateTimeField(verbose_name=_('Дата окончания'))
    is_active = models.BooleanField(
        default=False, verbose_name=_('Активная скидка')
    )
    percent_discount = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True,
        verbose_name=_('Скидка по процентам'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    value_discount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        verbose_name=_('Скидка по значению'),
        validators=[MinValueValidator(0)]
    )
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True, verbose_name='URL (slag)'
    )

    class Meta:
        verbose_name = _('Скидка')
        verbose_name_plural = _('Скидки')
        ordering = ['id']

    def __str__(self):
        return self.name


class ProductModel(models.Model):
    """Модель продукта."""
    model = models.CharField(
        max_length=255, verbose_name=_('Название')
    )
    description = models.TextField(verbose_name=_('Описание'), blank=True)
    category = models.ForeignKey(
        CategoryModel, on_delete=models.CASCADE, verbose_name=_('Категория'),
        related_name='category_product'
    )
    characteristics = models.ManyToManyField(
        CharacteristicModel, related_name='product',
        verbose_name=_('Характеристики'))
    main_image = models.ForeignKey(
        'FilesModel', on_delete=models.CASCADE, related_name='image_product',
        verbose_name=_('Главное изображение'), blank=True, null=True)
    gallery = models.ManyToManyField(
        'FilesModel', related_name='gallery_product', blank=True,
        verbose_name=_('Галлерея'),
    )
    files = models.ManyToManyField(
        'FilesModel', related_name='files_product', blank=True,
        verbose_name=_('Файлы'),
    )
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True, verbose_name='URL (slag)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Дата создания')
    )
    limited_edition = models.BooleanField(
        default=False, verbose_name=_('Ограниченный тираж')
    )
    discounts = models.ManyToManyField(
        DiscountModel, related_name='product', blank=True,
        verbose_name=_('Скидки')
    )
    code = models.CharField(
        max_length=255, verbose_name=_('Артикул'), blank=True,
        unique=True
    )
    manufacturer = models.CharField(
        max_length=255, verbose_name=_('Производитель'), blank=True
    )
    is_active = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(
        verbose_name=_('Счетчик просмотров'), default=0
    )

    def __str__(self):
        return self.model

    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')
        ordering = ['id']


@receiver(pre_save, sender=ProductModel)
def product_clear_cache(sender, instance, **kwargs):
    """Функция очистки кэша при изменении модели продукта."""
    if instance.id is None:  # Будет создан новый объект
        pass
    else:
        # Сброс кэша по изменению перечисленных в условии полей
        previous = ProductModel.objects.filter(id=instance.id)
        if (
                previous.model != instance.model or
                previous.description != instance.description or
                previous.characteristics != instance.characteristics or
                previous.main_image != instance.main_image or
                previous.gallery != instance.gallery or
                previous.files != instance.files or
                previous.discounts != instance.discounts or
                previous.code != instance.code or
                previous.manufacturer != instance.manufacturer or
                previous.is_active != instance.is_active
        ):
            product_cache_key = 'product:{}'.format(instance.slug)
            if cache.get(product_cache_key) is not None:
                cache.delete(product_cache_key)


class FilesModel(models.Model):
    """Файлы, относящиеся к продукту в магазине."""
    hash = models.CharField(max_length=13, default=_createHash, unique=True)
    file = models.FileField(
        upload_to='Product_files/', verbose_name=_('Файлы'),
        blank=True, null=True, validators=[validate_size_file]
    )
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True,
        verbose_name='URL (slag)'
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.file.name

    def get_absolute_url(self):
        return

    def filename(self):
        return os.path.basename(self.file.path)

    class Meta:
        verbose_name = _('Файл')
        verbose_name_plural = _('Файлы')
        ordering = ['id']


class TagsModel(models.Model):
    """Теги товара."""
    name = models.CharField(max_length=255, verbose_name=_('Тег'))
    product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name='tags',
        verbose_name=_('Товар')
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ['id']


@receiver(post_save, sender=TagsModel)
def tags_clear_cache_tags_model(sender, instance, **kwargs):
    """Функция очистки кэша по сигналу при изменении модели TagsModel."""
    tags_cache_key = 'tags:{}'.format(instance.product.slug)
    if cache.get(tags_cache_key) is not None:
        cache.delete(tags_cache_key)


class ProductOnShopModel(models.Model):
    """Товар, находящийся в магазине.
    """
    shop = models.ForeignKey(
        ShopModel, on_delete=models.CASCADE, verbose_name=_('Магазин'),
        related_name='product_on_shop'
    )
    product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, verbose_name=_('Товар'),
        related_name='product_on_shop'
    )
    quantity = models.PositiveIntegerField(verbose_name=_('Количество'))
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_('Цена')
    )
    for_sale = models.BooleanField(
        default=False, verbose_name=_('Для продажи')
    )

    def __str__(self):
        return self.product.model

    class Meta:
        verbose_name = _('Товар магазина')
        verbose_name_plural = _('Товары магазина')
        ordering = ['id']


@receiver(pre_save, sender=ProductOnShopModel)
def review_clear_cache_product_on_shop(sender, instance, **kwargs):
    """
    Функция очистки кэша по сигналу при изменении полей
     price и for_sale модели ProductOnShopModel.
    """
    if instance.id is None:  # Будет создан новый объект
        pass
    else:
        previous = ProductOnShopModel.objects.get(id=instance.id)

        # Сброс кэша по изменению перечисленных в условии полей
        if (previous.price != instance.price or
                previous.for_sale != instance.for_sale):
            slug = instance.product.slug
            product_on_shops_cache_key = 'product_on_shops:{}'.format(slug)
            min_price_cache_key = 'min_price_cache_key:{}'.format(slug)
            if cache.get(product_on_shops_cache_key) is not None:
                cache.delete(product_on_shops_cache_key)
                cache.delete(min_price_cache_key)


class ProductGroupModel(models.Model):
    """Группы товара."""
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    product = models.ForeignKey(
        ProductOnShopModel, on_delete=models.CASCADE,
        verbose_name=_('Товар'),
        related_name='product_group'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Группа товаров')
        verbose_name_plural = _('Группы товаров')
        ordering = ['id']


class ReviewModel(models.Model):
    """Отзывы, оценки товара."""
    product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name='review',
        verbose_name=_('Товар')
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='review',
        verbose_name=_('Пользователь')
    )
    review = models.TextField(
        max_length=510, verbose_name=_('Отзыв'), blank=True
    )
    is_active = models.BooleanField(default=True)
    add_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.review

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['id']


@receiver(post_save, sender=ReviewModel)
def review_clear_cache_review_model(sender, instance, **kwargs):
    """Функция очистки кэша по сигналу при изменении модели отзывов."""
    slug = instance.product.slug
    count_comments_cache_key = 'count_comments:{}'.format(slug)
    all_comments_cache_key = 'all_comments_cache_key:{}'.format(slug)
    comments_cache_key = 'comments_cache_key:{}'.format(slug)
    if cache.get(count_comments_cache_key) is not None:
        cache.delete(count_comments_cache_key)
    if cache.get(all_comments_cache_key) is not None:
        cache.delete(all_comments_cache_key)
    if cache.get(comments_cache_key) is not None:
        cache.delete(comments_cache_key)


class CartProductModel(models.Model):
    """Товар в корзине."""
    product = models.ForeignKey(
        ProductOnShopModel, on_delete=models.CASCADE,
        verbose_name=_('Товар'),
        related_name='cart_product',
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('Пользователь'),
        related_name='cart_product'
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_('Количество'), default=0
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_('Итого')
    )

    def __str__(self):
        return f'{_("Товар")}: {self.product.product.model}'

    class Meta:
        verbose_name = _('Товар в корзине')
        verbose_name_plural = _('Товары в корзине')
        ordering = ['id']


class CartModel(models.Model):
    """Модель хранения товаров в Корзина."""
    STATUS = (
        ('actively', _('Активно')),
        ('completed', _('Завершено')),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name='cart',
        verbose_name=_('Пользователь'),
    )
    products = models.ManyToManyField(
        CartProductModel, related_name='cart', default=None,
        verbose_name=_('Товар')
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_('Количество'), default=0
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_('Общая цена товаров'),
    )
    discount = models.ManyToManyField(
        DiscountModel, related_name='cart', blank=True,
        verbose_name=_('Скидка'),
    )
    status = models.CharField(
        max_length=9, choices=STATUS, default='actively',
        verbose_name=_('Статус')
    )

    def __str__(self):
        return f'{_("Корзина пользоватея")} {self.user.email}'

    class Meta:
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзины')
        ordering = ['id']


class OrderModel(models.Model):
    """Модели хранения информации о заказах."""
    STATUS = (
        ('actively', _('Активно')),
        ('completed', _('Завершено')),
    )

    PAYMENT = (
        ('online', _('Платеж картой')),
        ('someone', _('Платеж со случайного счета')),
    )

    cart = models.ForeignKey(
        CartModel, on_delete=models.CASCADE, verbose_name=_('Корзина'),
        related_name='order'
    )
    delivery_for_order = models.ForeignKey(
        'DeliveryModel', blank=True, null=True, on_delete=models.CASCADE,
        verbose_name=_('Доставка')
    )
    payment_type = models.CharField(
        max_length=7, choices=PAYMENT, default='online',
        verbose_name=_('Тип платежа')
    )
    payment_for_order = models.ForeignKey(
        'PaymentModel', blank=True, null=True, on_delete=models.CASCADE,
        verbose_name=_('Платеж')
    )
    date_order = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=9, choices=STATUS, default='actively',
        verbose_name=_('Статус')
    )
    country = models.CharField(
        max_length=255, verbose_name=_('Страна'), blank=True
    )
    locality = models.CharField(
        max_length=255, verbose_name=_('Город')
    )
    street = models.CharField(max_length=255, verbose_name=_('Улица'))
    house = models.CharField(max_length=255, verbose_name=_('Дом'))
    apartment = models.CharField(
        max_length=255, verbose_name=_('Квартира'), blank=True
    )
    entrance = models.CharField(
        max_length=255, verbose_name=_('Подъезд'), blank=True
    )
    floor = models.CharField(
        max_length=255, verbose_name=_('Этаж'), blank=True
    )
    order_total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_('Сумма заказа'),
    )

    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')
        ordering = ['id']

    def __str__(self):
        return f'{_("Заказ")} №{self.pk}, {_("Пользовтаеля")}:' \
               f' {self.cart.user.email}'


class ProductViewHistoryModel(models.Model):
    """История просмотра."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='view_history',
        verbose_name=_('Пользователь')
    )
    product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name='view_history',
        verbose_name=_('Посмотренный товар')
    )

    class Meta:
        verbose_name = _('История просмотра')
        verbose_name_plural = _('Истории просмотров')
        ordering = ['id']

    def __str__(self):
        return f'{self.user.email}{_(", товар: ")}{self.product.model}'


class PurchaseHistoryModel(models.Model):
    """История покупок."""
    order = models.ForeignKey(
        OrderModel, on_delete=models.CASCADE, verbose_name=_('Заказ'),
        related_name='purchase_history'
    )
    date_purchase = models.DateField(
        auto_now_add=True, verbose_name=_('Дата покупки')
    )

    class Meta:
        verbose_name = _('История покупок')
        verbose_name_plural = _('Истории покупок')
        ordering = ['id']

    def __str__(self):
        return f'{_("Заказ: ")}{self.order}{_(", Дата покупки: ")}' \
               f'{self.date_purchase}'


class DeliveryModel(models.Model):
    """Информация о доставке товаров."""
    TYPES = (
        ('default', _('Обычная доставка')),
        ('express', _('Экспресс доставка')),
    )

    delivery = models.CharField(
        max_length=255, verbose_name=_('Тип доставки'),
        choices=TYPES, default='default'
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_('Стоимость доставки')
    )
    express_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_('Наценка')
    )
    border_free_delivery = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name=_('Цена товаров для бесплатной доставки')
    )

    class Meta:
        verbose_name = _('Доставка')
        verbose_name_plural = _('Доставки')
        ordering = ['id']

    def __str__(self):
        return f'{self.get_delivery_display()}'


class PaymentModel(models.Model):
    """Информация об оплате товаров."""
    order = models.ForeignKey(
        OrderModel, on_delete=models.CASCADE, related_name='payment',
        verbose_name=_('Заказ')
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name=_('Цена с учетом доставки')
    )
    prove = models.BooleanField(
        default=False, verbose_name=_('Подтверждение оплаты')
    )

    class Meta:
        verbose_name = _('Оплата')
        verbose_name_plural = _('Оплата')
        ordering = ['id']

    def __str__(self):
        return f'{_("Заказ: ")}{self.order.pk}, ' \
               f'{_("цена: ")}{self.price}, {_("Оплачено")}: {self.prove}'


class StatusModel(models.Model):
    """Статус пользователей."""
    status = models.CharField(max_length=255, verbose_name=_('Статус'))
    shop = models.ForeignKey(
        ShopModel, on_delete=models.CASCADE, related_name='status',
        blank=True, null=True, verbose_name=_('Магазин'),
    )

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = _('Статус')
        verbose_name_plural = _('Статусы')
        ordering = ['id']


class BannerModel(models.Model):
    """Модель баннер на главной странице."""
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    description = models.TextField(
        max_length=1020, verbose_name=_('Описание')
    )
    image = models.ForeignKey(
        FilesModel, on_delete=models.CASCADE, blank=True, null=True,
        verbose_name=_('Изображение баннера')
    )
    shop_product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name='product_banner',
        verbose_name=_('Товар')
    )
    weight = models.PositiveIntegerField(
        verbose_name=_('Приоритет'), validators=[MaxValueValidator(10)]
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_('Активный слайдер')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Баннер')
        verbose_name_plural = _('Баннеры')
        ordering = ['id']
