from django.apps import AppConfig

class MetaConfig(AppConfig):
  name='voxel_globe.meta'
  def ready(self):
    import signals