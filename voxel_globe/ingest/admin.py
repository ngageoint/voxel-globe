from django.contrib import admin

from voxel_globe.ingest import models

### import meta.admin #Get some common admin tricks

# Register your models here.

admin.site.register(models.UploadSession)
admin.site.register(models.Directory)
admin.site.register(models.File)
