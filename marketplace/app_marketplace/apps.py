from django.apps import AppConfig


class AppMarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_marketplace'
    verbose_name = 'Торговая площадка'


class ImportExportCeleryConfig(AppConfig):
    name = 'import_export_celery'
    verbose_name = 'Работа с импортом'
