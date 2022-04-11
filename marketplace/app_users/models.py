from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def get_default_avatar():
    """Функция возврата пути расположения изображения профиля по умолчанию."""
    return "default_avatar/default_avatar.jpg"


def validate_size_image(file_obj):
    """Функция проверки размера файла."""
    megabyte_limit = 2
    if file_obj.size > megabyte_limit * 1024 * 1024:
        raise ValidationError(
            f'{_("Максимальный размер файла")} {megabyte_limit} MB'
        )


class User(AbstractUser):
    """Модель пользователя."""
    avatar = models.ImageField(
        upload_to='User_avatars/',
        default=get_default_avatar,
        verbose_name=_('Аватар'),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg']),
            validate_size_image
        ],
        blank=True
    )
    phone = models.CharField(
        max_length=12, unique=True, verbose_name=_('Телефон')
    )
    email_ver = models.BooleanField(
        default=False, verbose_name=_('Электронная почта подтверждена')
    )
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True, verbose_name='URL (slag)'
    )
    status = models.ForeignKey(
        to='app_marketplace.StatusModel',
        on_delete=models.CASCADE,
        verbose_name=_('Статус пользователя'),
        related_name='user',
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    email = models.EmailField(unique=True)

    def phone_number(self):
        return ' '.join(
            [
                '+7', f'({self.phone[0:3]})',
                f'{self.phone[3:6]}-{self.phone[6:8]}-{self.phone[8:10]}'
            ]
        )

    def get_absolute_url(self):
        return reverse('account', kwargs={'slug': self.slug})
