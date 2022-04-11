from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse, resolve
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from app_users.models import User
from app_users.views import LoginView, RegistrationView, AccountView, \
    ProfileView, ProductHistoryView, \
    OrderHistoryView


class TestUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin', slug='admin')

        cls.public_urls = (
            (reverse('account', args=['admin']), AccountView,
             'app_users/account.html'),
            (reverse('account_update', args=['admin']), ProfileView,
             'app_users/profile.html'),
            (reverse('history_products', args=['admin']), ProductHistoryView,
             'app_users/view_history_products.html'),
            (reverse('history_orders', args=['admin']), OrderHistoryView,
             'app_users/order_history_list.html'),
            (reverse('login'), LoginView, 'app_users/login.html'),
            (reverse('logout'), LogoutView, None),
            (reverse('registration'), RegistrationView,
             'app_users/registration.html'),
            (reverse('password_change_done'),
             auth_views.PasswordChangeDoneView, None),
            (reverse('password_change'), auth_views.PasswordChangeView, None),
            (reverse('password_reset_done'),
             auth_views.PasswordResetCompleteView, None),
            (reverse('password_reset'), auth_views.PasswordResetView, None),
            (reverse('password_reset_complete'),
             auth_views.PasswordResetCompleteView, None),
            (reverse('password_reset_confirm', args=[
                '95c0b50ebebf8e226fb832d0acb8adec53e84bd3',
                '95c0b50ebebf8e226fb832d0acb8adec53e84bd3']),
             auth_views.PasswordResetConfirmView, None),
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_url_is_resolved(self):
        for url, view, template in self.public_urls:
            if template is not None:
                if 'admin' in url:
                    c = self.auth_client
                else:
                    c = self.guest_client
                response = c.get(url)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEquals(resolve(url).func.view_class, view)
