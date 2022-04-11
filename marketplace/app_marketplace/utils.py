from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ValidationError


def validate_size_image(file_obj):
    """Функция проверки размера загруженного изображения."""
    megabyte_limit = 2
    if file_obj.size > megabyte_limit * 1024 * 1024:
        raise ValidationError(f'Максимальный размер файла {megabyte_limit} MB')


def validate_size_file(file_obj):
    """Функция проверки размера загруженного файла."""
    megabyte_limit = 10
    if file_obj.size > megabyte_limit * 1024 * 1024:
        raise ValidationError(f'Максимальный размер файла {megabyte_limit} MB')


def clear_cache(cache_name):
    assert settings.CACHES
    caches[cache_name].clear()
