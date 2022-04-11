from unittest import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from app_users.models import User, validate_size_image


class TestModels(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user = User.objects.create(email='tigr@admin.ru',
                                       username='tigr',
                                       phone='9122222222',
                                       slug='tigr')

    def test_upload_default_avatar(self):
        self.assertEqual(self.user.avatar,
                         "default_avatar/default_avatar.jpg")

    def test_validate_size_image(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        image_name = 'small.jpg'

        uploaded = SimpleUploadedFile(
            name=image_name,
            content=small_gif,
            content_type='image/jpg',
        )
        uploaded.size = 3 * 1024 * 1024
        with self.assertRaises(ValidationError) as cm:
            validate_size_image(uploaded)
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code,
                             'Максимальный размер файла 2 MB')

    def test_phone_number_return(self):
        self.assertEqual(self.user.phone_number(), '+7 (912) 222-22-22')

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), '/account/user/tigr/')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()
