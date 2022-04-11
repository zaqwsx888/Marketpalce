import os
from pathlib import Path
from decouple import config
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG')

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'app_marketplace.apps.AppMarketplaceConfig',
    'app_users.apps.AppUsersConfig',
    'app_marketplace.apps.ImportExportCeleryConfig',
    'pay_api.apps.PayApiConfig',
    'import_export',
    # 'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'author.middlewares.AuthorDefaultBackendMiddleware'
]

ROOT_URLCONF = 'marketplace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app_marketplace.context_processors.categories',
                'app_marketplace.context_processors.total_compared_items',
                'app_marketplace.context_processors.cart_information',
            ],
            'libraries': {
                'template_filters':
                    'app_marketplace.templatetags.template_filters',
            }
        },
    },
]

WSGI_APPLICATION = 'marketplace.wsgi.application'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

    # Только при разработке
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    DATABASES = {
        'default': env.db(),
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]
else:
    STATIC_ROOT = BASE_DIR / 'static'

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'app_users.User'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = '/'

CACHED_TIME = 600
SHOP_INFO_CACHE_TIME = 0
CATEGORIES_CACHE_TIME = 0

INTERNAL_IPS = [
    '127.0.0.1',
]

CART_SESSION_ID = 'cart'

# celery
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
# CELERY_RESULT_EXTENDED = True   # для получения переданных аргументов в task
CELERY_BEAT_SCHEDULE = {
    "sample_task": {
        "task": "app_marketplace.tasks.change_status_all_jobs",
        "schedule": crontab(minute="*/30"),
    },
}
IMPORT_EXPORT_CELERY_MODELS = {
    "ProductModel": {
        'app_label': 'app_marketplace',
        'model_name': 'ProductModel',
    }
}


def get_base_url():
    if DEBUG:
        return 'http://127.0.0.1:8000'
    return ''
