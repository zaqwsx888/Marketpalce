from django.test import TestCase
from app_users.forms import LoginForm, RegistrationForm, EditProfileForm
from app_users.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


class TestLoginForm(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create(email='rick@admin.ru',
                                       password='AdminAdmin12')

    def test_login_form_invalid_email(self):
        form_login = LoginForm(data={'email': 'admin1@admin.ru',
                                     'password': 'AdminAdmin12'})
        self.assertEqual(form_login.errors['__all__'][0],
                         'Пользователь с admin1@admin.ru не найден.')

    def test_login_form_invalid_password(self):
        form_login = LoginForm(data={'email': 'rick@admin.ru',
                                     'password': 'Admin'})
        self.assertEqual(form_login.errors['__all__'][0], 'Неверный пароль')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()


class TestRegistrationForm(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create(email='rick@admin.ru',
                                       password='AdminAdmin12')

    def setUp(self) -> None:
        self.data_reg = {'first_name': 'testname',
                         'last_name': 'testlastname',
                         'phone': '+79122222222',
                         'email': 'mail@mail.ru',
                         'password': 'AdminAdmin12',
                         'confirm_password': 'AdminAdmin12'}

    def test_registration_form_valid_data(self):
        form_reg = RegistrationForm(data=self.data_reg)
        self.assertTrue(form_reg.is_valid)

    def test_registration_form_invalid_phone(self):
        self.data_reg['phone'] = '+791222'
        form_reg = RegistrationForm(data=self.data_reg)
        self.assertEqual(form_reg.errors['phone'][0],
                         'Не верный телефон')

    def test_registration_form_invalid_email(self):
        self.data_reg['email'] = 'mail@mail.net'
        form_reg = RegistrationForm(data=self.data_reg)
        self.assertEqual(form_reg.errors['email'][0],
                         'Регистрация через домен net невозможна')
        self.data_reg['email'] = self.user.email
        form_reg_v2 = RegistrationForm(data=self.data_reg)
        self.assertEqual(form_reg_v2.errors['email'][0],
                         'Этот email уже используется')

    def test_registration_form_invalid_password(self):
        self.data_reg['confirm_password'] = 'AdminAdmin1'
        form_reg = RegistrationForm(data=self.data_reg)
        self.assertEqual(form_reg.errors['__all__'][0], 'Пароли не совпадают')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()


class TestEditForm(TestCase):
    def setUp(self) -> None:
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        image_name = 'small.jpg'

        self.uploaded = SimpleUploadedFile(
            name=image_name,
            content=small_gif,
            content_type='image/jpg',
        )

        self.data_edit = {'fio': 'da da da',
                          'email': 'mail@mail.ru',
                          'phone': '+7 (912) 222-22-22',
                          'password': 'dadadad',
                          'confirm_password': 'dadadad',
                          'avatar': self.uploaded}

    def test_edit_form_valid_data(self):
        form_edit = EditProfileForm(data=self.data_edit)
        self.assertTrue(form_edit.is_valid())
