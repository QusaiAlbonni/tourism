from django.apps import AppConfig


class TranslationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'localizations'
    def ready(self) -> None:
        import localizations.signals