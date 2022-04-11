from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()
        cls.pay_url = reverse('payments_api')
        cls.valid_data_payment = {'order_number': 12,
                                  'bank_card': '12345678',
                                  'price': 10.0}
        cls.invalid_data_payment = {'order_number': 12,
                                    'bank_card': '01234567',
                                    'price': 10.0}

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_pay_with_valid_card(self):
        response = self.guest_client.post(self.pay_url,
                                          data=self.valid_data_payment)
        self.assertEquals(response.json(), {
            'order_number': self.valid_data_payment['order_number'],
            'status': 'paid'})
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pay_with_invalid_card(self):
        response = self.guest_client.post(self.pay_url,
                                          data=self.invalid_data_payment)
        self.assertEquals(response.json(), {
            'order_number': self.invalid_data_payment['order_number'],
            'status': 'error'})
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
