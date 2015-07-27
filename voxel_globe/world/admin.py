from django.contrib import admin
from voxel_globe.world.models import WorldBorder

class WorldBorderAdmin(admin.ModelAdmin):
  list_display = ('name', 'lat', 'lon', 'closeToUS');

# Register your models here.
admin.site.register(WorldBorder, WorldBorderAdmin)
