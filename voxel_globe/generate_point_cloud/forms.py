from django import forms
import voxel_globe.meta.models as models

class ErrorPointCloudOrderForm(forms.Form):
  voxel_world = forms.ModelChoiceField(label="Voxel World", 
      queryset=models.VoxelWorld.objects.all().order_by('name'))
  threshold = forms.FloatField(label="Threshold", min_value=0.0, max_value=1.0)
  position_error = forms.FloatField(label="Position error", help_text="blah", 
                                    min_value=0.0, required=False)
  orientation_error = forms.FloatField(label="Orientation error", help_text="blah blah", 
                                       min_value=0.0, required=False)
