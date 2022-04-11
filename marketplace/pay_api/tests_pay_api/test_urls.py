from django.test import TestCase
from django.urls import reverse, resolve
from pay_api.views import PaymentsAPIView


class TestUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.public_urls = (
            (reverse('payments_api'), PaymentsAPIView),)

    def test_url_is_resolved(self):
        for url, view in self.public_urls:
            self.assertEquals(resolve(url).func.view_class, view)
