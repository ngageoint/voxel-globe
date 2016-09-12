from django import forms
import voxel_globe.meta.models as models

class HeightProcessForm(forms.Form):
  image = forms.ModelChoiceField(label="Height image", 
      queryset=models.Image.objects.filter(name__startswith='Height Map').order_by('name'))

class HeightForm(forms.Form):
  voxel_world = forms.ModelChoiceField(label="Voxel World", 
      queryset=models.VoxelWorld.objects.all().order_by('name'))
  render_height = forms.FloatField(
      label="Render Height (optional)", required=False)