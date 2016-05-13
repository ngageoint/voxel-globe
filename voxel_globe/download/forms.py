from django import forms
import voxel_globe.meta.models as models

class TiePointForm(forms.Form):
  image_collection = forms.ModelChoiceField(label="Image Collection", 
      queryset=models.ImageCollection.objects.all().order_by('name'))

class PointCloudForm(forms.Form):
  point_cloud = forms.ModelChoiceField(label="Point Cloud", 
      queryset=models.PointCloud.objects.all().order_by('name'))

class ImageForm(forms.Form):
  image = forms.ModelChoiceField(label="Image", 
      queryset=models.Image.objects.all().order_by('name'))
