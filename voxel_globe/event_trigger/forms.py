from django import forms
import voxel_globe.meta.models as models

class EventTriggerForm(forms.Form):
  site = forms.ModelChoiceField(label="Site", 
      queryset=models.SattelSite.objects.all().order_by('name'))
