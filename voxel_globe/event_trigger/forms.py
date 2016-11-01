from django import forms
import voxel_globe.meta.models as models

class EventTriggerForm(forms.Form):
  sites = models.SattelSite.objects.exclude(satteleventtrigger=None) \
      .order_by('name')
  site = forms.ModelChoiceField(label="Site", queryset=sites)
