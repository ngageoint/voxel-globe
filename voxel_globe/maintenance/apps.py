from django.apps import AppConfig
from .signals import prepare

#See https://github.com/un1t/django-cleanup/blob/master/django_cleanup/apps.py

class MaintenanceConfig(AppConfig):
  name = "maintenance"
  verbose_name = "Automatic Maintenance Routines"

  def ready(self):
    prepare()