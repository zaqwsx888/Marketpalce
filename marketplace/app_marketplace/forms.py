from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from app_marketplace.models import DeliveryModel, OrderModel
from django.utils.translation import gettext_lazy as _


def get_cache_choices():
    caches = settings.CACHES or {}
    return [
        (key, f"{key} ({cache['BACKEND']}") for key, cache in caches.items()
    ]


class ClearCacheForm(forms.Form):
    cache_name = forms.ChoiceField(
        choices=get_cache_choices, label=_('Выбор кэша')
    )


class CreateOrderDeliveryForm(forms.ModelForm):
    delivery_for_order = forms.ModelChoiceField(
        queryset=DeliveryModel.objects.all(),
        widget=forms.RadioSelect,
        label="",
    )
    country = forms.CharField(max_length=255, label=_('Страна'),
                              required=False)
    locality = forms.CharField(max_length=255, label=_('Город'),
                               required=True)
    street = forms.CharField(max_length=255, label=_('Улица'), required=True)
    house = forms.CharField(max_length=255, label=_('Дом'), required=True)
    apartment = forms.CharField(max_length=255, label=_('Квартира'),
                                required=True)
    entrance = forms.CharField(max_length=255, label=_('Подъезд'),
                               required=False)
    floor = forms.CharField(max_length=255, label=_('Этаж'), required=False)

    class Meta:
        model = OrderModel
        fields = (
            'delivery_for_order', 'country', 'locality', 'street', 'house',
            'apartment', 'entrance', 'floor'
        )


class CreateOrderPaymentForm(forms.ModelForm):
    payment_type = forms.ChoiceField(
        choices=OrderModel.PAYMENT,
        widget=forms.RadioSelect,
        label="",
        initial="online"
    )

    class Meta:
        model = OrderModel
        fields = ('payment_type',)


class CreatePaymentForm(forms.Form):
    card_number = forms.CharField(max_length=9)

    def clean_cart_number(self):
        cart = self.cleaned_data['cart_number']
        try:
            cart_number = int(cart)
            if cart_number % 2 != 0:
                raise ValidationError(_('Введено нечетное число'))
        except ValueError:
            raise ValidationError(_('Введите целое число'))
