from django import forms
import voxel_globe.meta.models as models

class CreateSiteForm(forms.Form):
  name = forms.CharField(label="Site Name")

  south_d = forms.FloatField(label="South Latitude", help_text="degrees")
  west_d = forms.FloatField(label="West Longitude", help_text="degrees")
  bottom_d = forms.FloatField(label="Bottom Altitude", help_text="meters")
  north_d = forms.FloatField(label="North Latitude", help_text="degrees")
  east_d = forms.FloatField(label="East Longitude", help_text="degrees")
  top_d = forms.FloatField(label="Top Altitude", help_text="meters")

  south_d.widget.attrs['class'] = 'bbox degree'
  west_d.widget.attrs['class'] = 'bbox degree'
  bottom_d.widget.attrs['class'] = 'bbox degree'
  north_d.widget.attrs['class'] = 'bbox degree'
  east_d.widget.attrs['class'] = 'bbox degree'
  top_d.widget.attrs['class'] = 'bbox degree'