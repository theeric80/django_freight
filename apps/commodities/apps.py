from django.apps import AppConfig


class CommoditiesConfig(AppConfig):
    name = 'apps.commodities'

    def ready(self):
        from apps.commodities import signals
