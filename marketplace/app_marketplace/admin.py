from django.contrib import admin
from django.contrib.admin import display
from django.utils.safestring import mark_safe
from .models import (
    CharacteristicModel, CategoryModel, ValueModel, CharacteristicNameModel,
    ShopAddressModel, ShopModel, TypeOfDiscountModel, DiscountModel,
    ProductModel, ProductOnShopModel, FilesModel, TagsModel, ProductGroupModel,
    ReviewModel, CartProductModel, CartModel, OrderModel,
    ProductViewHistoryModel, PurchaseHistoryModel, DeliveryModel, PaymentModel,
    StatusModel, BannerModel
)
from import_export.admin import (
    ImportExportModelAdmin, ExportMixin, ImportExportMixin
)


@admin.register(CharacteristicModel)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id',)
    list_display_links = ('id',)
    search_fields = ('name',)


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'is_active')
    ordering = ('id',)
    list_filter = ('id', 'is_active')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ValueModel)
class ValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'value',)
    ordering = ('id',)
    list_filter = ('value',)
    list_display_links = ('id', 'value')
    search_fields = ('value',)


@admin.register(CharacteristicNameModel)
class CharacteristicNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    ordering = ('id',)
    list_filter = ('name',)
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(ShopAddressModel)
class ShopAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'country', 'city', 'street', 'house', 'floor')
    ordering = ('id',)
    list_display_links = ('id',)
    search_fields = ('country', 'city', 'street', 'house')


@admin.register(ShopModel)
class ShopAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'description', 'image', 'phone', 'email', 'slug'
    )
    ordering = ('id',)
    list_display_links = ('id', 'name')
    search_fields = ('name', 'email', 'phone')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['shop_logo']

    @classmethod
    def shop_logo(cls, obj):
        return mark_safe(f'<img src="{obj.image.file.url}"/>')


@admin.register(TypeOfDiscountModel)
class TypeOfDiscountAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'weight', 'is_active')
    ordering = ('id',)
    list_filter = ('is_active',)
    list_display_links = ('id', 'name')
    search_fields = ('name',)

    def has_add_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        else:
            return True

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        else:
            return True


@admin.register(DiscountModel)
class DiscountAdmin(ImportExportModelAdmin):
    list_display = (
        'id', 'name', 'description', 'slug', 'type_of_discount',
        'percent_discount', 'value_discount', 'date_start', 'date_end',
        'is_active'
    )
    ordering = ('id',)
    list_filter = ('date_start', 'date_end', 'is_active')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductModel)
class ProductAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        'id', 'model', 'description', 'category', 'slug',
        'created_at', 'limited_edition'
    )
    ordering = ('id',)
    list_display_links = ('id', 'model')
    search_fields = ('model',)
    prepopulated_fields = {'slug': ('model',)}


@admin.register(ProductOnShopModel)
class ProductOnShopAdmin(ImportExportModelAdmin):
    list_display = ('id', 'product', 'shop', 'quantity', 'price', 'for_sale')
    ordering = ('id',)
    list_filter = ('for_sale',)
    list_display_links = ('id', 'product',)
    search_fields = ('product__model',)


@admin.register(FilesModel)
class FilesAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'slug', 'is_active')
    ordering = ('id',)
    list_filter = ('is_active',)
    list_display_links = ('id', 'file')
    search_fields = ('file',)
    prepopulated_fields = {'slug': ('file',)}


@admin.register(TagsModel)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product', 'is_active')
    ordering = ('id',)
    list_filter = ('is_active',)
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(ProductGroupModel)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product', 'is_active')
    ordering = ('id',)
    list_filter = ('is_active',)
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(ReviewModel)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'review', 'is_active')
    ordering = ('id',)
    list_filter = ('is_active',)
    list_display_links = ('id', 'product', 'user')
    search_fields = ('rating',)


@admin.register(CartProductModel)
class CartProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'quantity', 'price')
    ordering = ('id',)
    list_display_links = ('id', 'product', 'user')
    search_fields = ('product', 'user',)


@admin.register(CartModel)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quantity', 'total_price', 'status')
    ordering = ('id',)
    list_filter = ('status',)
    list_display_links = ('id', 'user')
    search_fields = ('user',)


@admin.register(OrderModel)
class OrderAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        'id', 'cart', 'status', 'country', 'locality', 'street',
        'house', 'apartment', 'entrance', 'floor'
    )
    ordering = ('id',)
    list_filter = ('status',)
    list_display_links = ('id', 'cart')
    search_fields = ('cart',)


@admin.register(ProductViewHistoryModel)
class ProductViewHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')
    ordering = ('id',)
    list_display_links = ('id', 'user', 'product')
    search_fields = ('user', 'product')


@admin.register(PurchaseHistoryModel)
class PurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order')
    ordering = ('id',)
    list_display_links = ('id', 'order')
    search_fields = ('order',)


@admin.register(DeliveryModel)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'delivery', 'price')
    ordering = ('id',)
    list_display_links = ('id', 'delivery')
    search_fields = ('delivery',)


@admin.register(PaymentModel)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'price', 'prove')
    ordering = ('id',)
    list_filter = ('prove',)
    list_display_links = ('id', 'order', 'price', 'prove')


@admin.register(StatusModel)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'shop')
    list_filter = ('status',)


@admin.register(BannerModel)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'get_product', 'weight')
    ordering = ('id',)
    list_display_links = ('id', 'name')
    list_filter = ('weight',)
    search_fields = ('name',)

    @display(ordering='banner__product_banner', description='Product')
    def get_product(self, obj):
        return obj.shop_product
