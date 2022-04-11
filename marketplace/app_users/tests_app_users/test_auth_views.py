from django.test import TestCase
from django.urls import reverse
from app_users.models import User


class BaseTest(TestCase):
    def setUp(self):
        self.register_url = reverse('registration')
        self.login_url = reverse('login')
        self.user = {
            'first_name': ['testname'],
            'last_name': ['testlastname'],
            'phone': ['+7 (912) 222-22-22'],
            'email': ['testmail@mail.ru'],
            'password': ['Admin123aa'],
            'confirm_password': ['Admin123aa']
        }

        return super().setUp()


class RegisterTest(BaseTest):
    def test_can_view_page_correctly(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/registration.html')

    def test_can_register_user(self):
        response = self.client.post(self.register_url, self.user,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_cant_register_user_with_unmatching_passwords(self):
        self.user['confirm_password'] = ['admin1']
        response = self.client.post(self.register_url, self.user,
                                    format='text/html')
        self.assertEqual(response.status_code, 400)

    def test_cant_register_user_with_invalid_passwords(self):
        self.user['password'], self.user['confirm_password'] = ['adm'], ['adm']
        response = self.client.post(self.register_url, self.user,
                                    format='text/html')
        self.assertEqual(response.status_code, 400)

    def test_cant_register_user_with_invalid_email(self):
        self.user['email'] = ['testmail.ru']
        response = self.client.post(self.register_url, self.user,
                                    format='text/html')
        self.assertEqual(response.status_code, 400)

    def test_cant_register_user_with_taken_email(self):
        self.client.post(self.register_url, self.user, format='text/html')
        response = self.client.post(self.register_url, self.user,
                                    format='text/html')
        self.assertEqual(response.status_code, 400)


class LoginTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(email='testmail@mail.ru',
                                            username='testmail',
                                            password='Admin123aa')
        cls.user.is_active = True
        cls.user.save()

    def test_can_access_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/login.html')

    def test_login_success(self):
        response = self.client.post(self.login_url, self.user,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_cantlogin_with_unverified_email(self):
        self.user['email'] = ['test@mail.ru']
        response = self.client.post(self.login_url, self.user,
                                    format='text/html')
        self.assertEqual(response.status_code, 401)

    def test_cantlogin_with_unverified_password(self):
        self.user['password'] = ['adm']
        response = self.client.post(self.login_url, self.user,
                                    format='text/html')
        self.assertEqual(response.status_code, 401)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
