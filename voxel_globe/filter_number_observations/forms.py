from django import forms
import voxel_globe.meta.models as models

class FilterNumberObservationsForm(forms.Form):
  voxel_world = forms.ModelChoiceField(label="Voxel World", 
      queryset=models.VoxelWorld.objects.all().order_by('name'))
  number_means = forms.FloatField(min_value=0,
      label="Mean Multiplier", required=True)