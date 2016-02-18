from django import forms
import voxel_globe.meta.models as models

class HeightProcessForm(forms.Form):
  image = forms.ModelChoiceField(label="Height image", 
      queryset=models.Image.objects.filter(name__startswith='Height Map', 
          newerVersion=None).order_by('name'))