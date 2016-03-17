from django import forms
import voxel_globe.meta.models as models

class HeightForm(forms.Form):
  voxel_world = forms.ModelChoiceField(label="Voxel World", 
      queryset=models.VoxelWorld.objects.all().order_by('name'))
  render_height = forms.FloatField(
      label="Render Height (optional)", required=False)