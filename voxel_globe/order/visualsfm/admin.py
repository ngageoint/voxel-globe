from django.contrib import admin

from voxel_globe.order.visualsfm import models

# Register your models here.

admin.site.register(models.Order)
admin.site.register(models.Session)