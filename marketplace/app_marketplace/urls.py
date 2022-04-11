from django.urls import path
from app_marketplace import views
from app_marketplace.views import SearchProductsView
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main'),
    path('shop/', views.ShopListView.as_view(), name='shop_list'),
    path('shop/<slug:slug>/', views.ShopDetailView.as_view(), name='shop'),
    path('catalog/', views.CategoryListView.as_view(), name='category_list'),
    path('catalog/<slug:slug>/', views.CategoryCatalogView.as_view(),
         name='catalog'),
    path('order/', views.UserOrderView.as_view(), name='user_order'),
    path('order/create/', views.CreateOrderDeliveryView.as_view(),
         name='create_order_delivery'),
    path('order/payments/', views.CreateOrderPaymentView.as_view(),
         name='create_order_payments'),
    path('order/confirm/', views.ConfirmOrderView.as_view(),
         name='confirm_order'),
    path('order/delivery/', views.DeliveryInfoView.as_view(),
         name='delivery'),
    path('order/payment/', views.CreatePayment.as_view(),
         name='create_payment'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(),
         name='good_details'),
    path('compare/', views.CompareView.as_view(), name='compare'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('discounts/', views.DiscountsListView.as_view(), name='discounts'),
    path('discounts/<slug:discount_slug>/', views.DiscountDetailView.as_view(),
         name='discount_detail'),
    path('add-cart-product/', views.DynamicAddProductToCart.as_view(),
         name='add_cart_product'),
    path('change-cart-product/', views.DynamicChangeProductToCart.as_view(),
         name='change_cart_product'),
    path('search_products/', SearchProductsView.as_view(),
         name='search_products'),
    path('contact/', TemplateView.as_view(
        template_name="app_marketplace/contact.html"), name='contact'),
]
