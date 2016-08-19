from django.contrib import admin
from voxel_globe.websockets import models

# Register your models here.
admin.site.register(models.LogMessage)