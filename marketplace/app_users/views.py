import random
from django import views
from django.contrib.auth import authenticate, login
from django.db.models import Min, Max, IntegerField
from django.http import HttpResponseRedirect
from django.shortcuts import render
from app_users.forms import LoginForm, RegistrationForm, EditProfileForm
from app_users.models import User
from app_marketplace.services import (
    GetPurchaseHistoryService, AddLookedProductsService,
    GetDiscountsForProductsService, AddItemToCart
)
from app_marketplace.models import (
    ProductModel, CartProductModel, CartModel, OrderModel
)
from django.views.generic import DetailView, TemplateView, ListView
from app_marketplace.cart import Cart


class LoginView(views.View):
    """Представление авторизации пользователя."""
    @classmethod
    def get(cls, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'app_users/login.html', context)

    @classmethod
    def post(cls, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                cart_session = Cart(request)
                if cart_session.__len__() != 0:
                    for product in cart_session:
                        cart = CartModel.objects.filter(
                            user=user, status='actively').prefetch_related(
                            'products').first()
                        obj, created = \
                            CartProductModel.objects.update_or_create(
                                product=product['product'], user=user)
                        if created:
                            AddItemToCart().add_item_to_cart(
                                cart=cart,
                                product=obj,
                                amount=product['quantity'],
                                price=product['product'].price * product[
                                    'quantity']
                            )

                        else:
                            AddItemToCart().change_item_count_cart(
                                request=request,
                                product=obj.product,
                                count=product['quantity']
                            )

                        cart_session.delete(product['product'])

                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'app_users/login.html', context, status=401)


class RegistrationView(views.View):
    """Регистрация пользователя."""
    template_name = 'app_users/registration.html'
    success_url = '/'

    @classmethod
    def get(cls, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, cls.template_name, context)

    @classmethod
    def post(cls, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.set_password(form.cleaned_data['password'])
            new_user.username = new_user.email.split('@')[0] + str(
                random.randint(1, 900000))
            new_user.slug = new_user.username
            new_user.save()
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.save()
            login(request, user)
            return HttpResponseRedirect(cls.success_url)
        context = {
            'form': form
        }
        return render(request, cls.template_name, context, status=400)


class AccountView(DetailView):
    """Страница аккаунта."""
    model = User
    template_name = 'app_users/account.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        order_history = GetPurchaseHistoryService().get_orders_history(
            user=self.object)
        if len(order_history) > 0:
            context['order_history'] =\
                GetPurchaseHistoryService().get_orders_history(
                    user=self.object)[0]
        else:
            context['order_history'] = None

        looked_history =\
            AddLookedProductsService().get_a_list_of_viewed_products(
                user=self.object, quantity=3
            )
        products_list = [product.product.id for product in looked_history]

        products_on_shops = ProductModel.objects.select_related().annotate(
            min_price=Min(
                'product_on_shop__price', output_field=IntegerField()
            ),
            max_price=Max(
                'product_on_shop__price', output_field=IntegerField())
        ).filter(id__in=products_list)

        if len(products_on_shops):
            product_on_shops = [
                (GetDiscountsForProductsService.get_discount_price(
                    product=product, price=product.min_price)[0]
                 if product.discounts.exists() else product.min_price, product)
                for product in products_on_shops
            ]

            context['products'] = product_on_shops
        return context


class ProfileView(views.View):
    """Обновление аккаунта."""
    @classmethod
    def get(cls, request, *args, **kwargs):
        return render(request, 'app_users/profile.html')

    @classmethod
    def post(cls, request, *args, **kwargs):
        form = EditProfileForm(
            request.POST, request.FILES, instance=request.user
        )
        if form.is_valid():
            fio = form.cleaned_data['fio'].split()
            if len(fio) == 1:
                first_name, last_name = fio[0], ''
            else:
                first_name, last_name = fio[0], fio[1]
            new_user = User.objects.get(**kwargs)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.avatar = form.cleaned_data['avatar']
            new_user.phone = form.cleaned_data['phone']
            new_user.email = form.cleaned_data['email']
            new_user.save()
            if form.cleaned_data['password'] != '':
                new_user.set_password(form.cleaned_data['password'])
                new_user.save()
                user = authenticate(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                login(request, user)

        context = {'errors': form.errors.get_json_data()}
        return render(request, 'app_users/profile.html', context)


class ProductHistoryView(TemplateView):
    """История просмотров пользователя."""
    template_name = 'app_users/view_history_products.html'

    def get_context_data(self, **kwargs):
        context = super(ProductHistoryView, self).get_context_data(**kwargs)
        product_list =\
            AddLookedProductsService().get_a_list_of_viewed_products(
                self.request.user)

        products_list = [product.product.id for product in product_list]

        products_on_shops = ProductModel.objects.select_related().annotate(
            min_price=Min(
                'product_on_shop__price', output_field=IntegerField()
            ),
            max_price=Max(
                'product_on_shop__price', output_field=IntegerField())
        ).filter(id__in=products_list)

        if len(products_on_shops):
            product_on_shops = [
                (GetDiscountsForProductsService.get_discount_price(
                    product=product, price=product.min_price)[0]
                 if product.discounts.exists() else product.min_price, product)
                for product in products_on_shops
            ]

            context['products'] = product_on_shops

        return context


class OrderHistoryView(ListView):
    """История заказов пользователя."""
    model = OrderModel
    template_name = 'app_users/order_history_list.html'
    context_object_name = 'order_list'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(cart__user=self.request.user)


class OrderUserDetailView(DetailView):
    model = OrderModel
    template_name = 'app_users/user_order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(cart__user=self.request.user)
