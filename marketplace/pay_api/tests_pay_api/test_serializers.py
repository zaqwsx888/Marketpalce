from pay_api.serializers import PaymentSerializer
from django.test import TestCase


class TestSerializers(TestCase):
    def setUp(self):
        self.data_payment = {'order_number': 12,
                             'bank_card': '12345678',
                             'price': 10.0}

    def test_valid_data(self):
        serializer = PaymentSerializer(data=self.data_payment)
        self.assertTrue(serializer.is_valid())

    def test_invalid_order_number(self):
        self.data_payment['order_number'] = 0
        serializer = PaymentSerializer(data=self.data_payment)
        self.assertFalse(serializer.is_valid())

    def test_invalid_bank_card(self):
        numbers_card = ('123', '1234567999')
        for num in numbers_card:
            self.data_payment['bank_card'] = num
            serializer = PaymentSerializer(data=self.data_payment)
            self.assertFalse(serializer.is_valid())

    def test_invalid_price(self):
        prices = (123456789999.0, 10.1234)
        for price in prices:
            self.data_payment['price'] = price
            serializer = PaymentSerializer(data=self.data_payment)
            self.assertFalse(serializer.is_valid())
