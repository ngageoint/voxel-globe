from django import forms

class UploadFileForm(forms.Form):
  title = forms.CharField(max_length=250);
  file1 = forms.FileField();
  