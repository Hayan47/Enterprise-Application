from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'files'

from django_celery_beat import apps as celery_beat_apps

class MyConfig(AppConfig):
  name = 'files'
  
  def ready(self):
    celery_beat_apps.BeatConfig()