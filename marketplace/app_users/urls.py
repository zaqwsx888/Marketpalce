from django.contrib.auth.views import LogoutView
from django.urls import path
from django.contrib.auth import views as auth_views
from app_users.views import (
    LoginView, RegistrationView, AccountView, ProfileView,
    ProductHistoryView, OrderHistoryView, OrderUserDetailView
)

urlpatterns = [
    path('user/<slug:slug>/', AccountView.as_view(), name='account'),
    path('user/<slug:slug>/edit/', ProfileView.as_view(),
         name='account_update'),
    path('user/<slug:slug>/history_products/', ProductHistoryView.as_view(),
         name='history_products'),
    path('user/<slug:slug>/history_orders/', OrderHistoryView.as_view(),
         name='history_orders'),
    path('user/<slug:slug>/history_orders/<int:pk>/',
         OrderUserDetailView.as_view(), name='user_order_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), {'next_page': '/'}, name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='app_users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='app_users/password_change.html'),
        name='password_change'
    ),
    path('password_reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='app_users/password_reset_done.html'),
         name='password_reset_done'),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='app_users/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='app_users/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
