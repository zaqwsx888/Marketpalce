from django.test import TestCase
from app_marketplace.forms import CreateOrderDeliveryForm, \
    CreateOrderPaymentForm, CreatePaymentForm
from app_marketplace.models import DeliveryModel


class TestForms(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.delivery = DeliveryModel.objects.create(delivery='default',
                                                    price=10.0,
                                                    border_free_delivery=5000.0)
        cls.data_valid_delivery = {
            'delivery_for_order': str(cls.delivery.id), 'country': 'unknown',
            'locality': 'unknown', 'street': 'unknown',
            'house': 'unknown', 'entrance': 'unknown',
            'floor': 'unknown', 'apartment': '1'}

        cls.data_valid_payment = [{
            'payment_type': 'online'
        }, {
            'payment_type': 'someone'
        }]

    def test_create_order_delivery_form(self):
        form = CreateOrderDeliveryForm(data=self.data_valid_delivery)
        self.assertTrue(form.is_valid())

    def test_create_order_payment_form(self):
        for data_payment in self.data_valid_payment:
            form = CreateOrderPaymentForm(data=data_payment)
            self.assertTrue(form.is_valid())

    def test_create_payment_form(self):
        form = CreatePaymentForm(data={'card_number': '111111111'})
        self.assertTrue(form.is_valid())
