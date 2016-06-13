from django import forms
import voxel_globe.meta.models as models

class OrderVoxelWorldBaseForm(forms.Form):
  image_set = forms.ModelChoiceField(label="Image Set", 
      queryset=models.ImageSet.objects.all().order_by('name'))
  camera_set = forms.ModelChoiceField(label="Camera Set",
      queryset=models.CameraSet.objects.all().order_by('name'))
  scene = forms.ModelChoiceField(label="Scene", 
      queryset=models.Scene.objects.all().order_by('name'))
  regularization = forms.BooleanField(label="Regularize?", required=False)

  #refines = forms.IntegerField(label="Number of refines?", min_value=0)

class OrderVoxelWorldDegreeForm(forms.Form):
  south_d = forms.FloatField(label="South Latitude", help_text="degrees")
  west_d = forms.FloatField(label="West Longitude", help_text="degrees")
  bottom_d = forms.FloatField(label="Bottom Altitude", help_text="meters")
  north_d = forms.FloatField(label="North Latitude", help_text="degrees")
  east_d = forms.FloatField(label="East Longitude", help_text="degrees")
  top_d = forms.FloatField(label="Top Altitude", help_text="meters")
  voxel_size_d = forms.FloatField(label="Voxel Size", help_text="meters", min_value=0)

  south_d.widget.attrs['class'] = 'bbox degree'
  west_d.widget.attrs['class'] = 'bbox degree'
  bottom_d.widget.attrs['class'] = 'bbox degree'
  north_d.widget.attrs['class'] = 'bbox degree'
  east_d.widget.attrs['class'] = 'bbox degree'
  top_d.widget.attrs['class'] = 'bbox degree'
  voxel_size_d.widget.attrs['class'] = 'degree'

class OrderVoxelWorldMeterForm(forms.Form):
  south_m = forms.FloatField(label="South", help_text="meters")
  west_m = forms.FloatField(label="West", help_text="meters")
  bottom_m = forms.FloatField(label="Bottom Altitude", help_text="meters")
  north_m = forms.FloatField(label="North", help_text="meters")
  east_m = forms.FloatField(label="East", help_text="meters")
  top_m = forms.FloatField(label="Top Altitude", help_text="meters")
  voxel_size_m = forms.FloatField(label="Voxel Size", help_text="meters", min_value=0)

  south_m.widget.attrs['class'] = 'bbox meter'
  west_m.widget.attrs['class'] = 'bbox meter'
  bottom_m.widget.attrs['class'] = 'bbox meter'
  north_m.widget.attrs['class'] = 'bbox meter'
  east_m.widget.attrs['class'] = 'bbox meter'
  top_m.widget.attrs['class'] = 'bbox meter'
  voxel_size_m.widget.attrs['class'] = 'meter'

class OrderVoxelWorldUnitForm(forms.Form):
  south_u = forms.FloatField(label="South", help_text="units")
  west_u = forms.FloatField(label="West", help_text="units")
  bottom_u = forms.FloatField(label="Bottom Altitude", help_text="units")
  north_u = forms.FloatField(label="North", help_text="units")
  east_u = forms.FloatField(label="East", help_text="units")
  top_u = forms.FloatField(label="Top Altitude", help_text="units")
  voxel_size_u = forms.FloatField(label="Voxel Size", help_text="units", min_value=0)

  south_u.widget.attrs['class'] = 'bbox unit'
  west_u.widget.attrs['class'] = 'bbox unit'
  bottom_u.widget.attrs['class'] = 'bbox unit'
  north_u.widget.attrs['class'] = 'bbox unit'
  east_u.widget.attrs['class'] = 'bbox unit'
  top_u.widget.attrs['class'] = 'bbox unit'
  voxel_size_u.widget.attrs['class'] = 'unit'
