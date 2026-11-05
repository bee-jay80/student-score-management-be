from django.apps import AppConfig


class GradesConfig(AppConfig):
    name = 'apps.grades'
    
    def ready(self):
        import apps.grades.signals
