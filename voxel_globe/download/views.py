import os
from os import environ as env

from django.shortcuts import render, redirect, HttpResponse
from django.core import serializers

import voxel_globe.download.forms as forms

from .tools import xfilesend_response

# Create your views here.
def index(request):
  return render(request, 'download/html/index.html',
                {'title': 'Voxel Globe - Download',
                 'page_title': 'Voxel Globe - Download'})

def tiepoint(request):
  if request.method == 'POST':

    form = forms.TiePointForm(request.POST)

    if form.is_valid():
      image_collection = form.cleaned_data['image_collection']
      all_tiepoints = []
      for image in image_collection.images.all():
        tiepoints = image.tiepoint_set.all()
        for tiepoint in tiepoints:
          all_tiepoints.append(tiepoint)
      response =  HttpResponse(serializers.serialize('geojson', all_tiepoints))
      response['Content-Disposition'] = 'attachment; ' + \
          'filename=tie_points_%d.json' % image_collection.id
      response['Content-Length'] = len(response.content)
      return response
  else:
    form = forms.TiePointForm()

  return render(request, 'main/form.html',
                {'title': 'Voxel Globe - Download',
                 'page_title': 'Voxel Globe - Download Tie Points ' + \
                               'for Image Collection',
                 'form':form})

def control_point(request):
  if request.method == 'POST':

    form = forms.TiePointForm(request.POST)

    if form.is_valid():
      image_collection = form.cleaned_data['image_collection']
      control_points = []
      for image in image_collection.images.all():
        tiepoints = image.tiepoint_set.all()
        for tiepoint in tiepoints:
          if tiepoint.geoPoint not in control_points:
            control_points.append(tiepoint.geoPoint)
      response = HttpResponse(serializers.serialize('geojson', control_points))
      response['Content-Disposition'] = 'attachment; ' + \
          'filename=control_points_%d.json' % image_collection.id
      response['Content-Length'] = len(response.content)
      return response
  else:
    form = forms.TiePointForm()

  return render(request, 'main/form.html',
                {'title': 'Voxel Globe - Download',
                 'page_title': 'Voxel Globe - Download Control Points for Image Collection',
                 'form':form})

def point_cloud_ply(request):
  if request.method == 'POST':
    form = forms.PointCloudForm(request.POST)
    if form.is_valid():
      point_cloud = form.cleaned_data['point_cloud']

      return xfilesend_response(request, point_cloud.filename,
          download_name='point_cloud_%d.ply' % point_cloud.id)
  else:
    form = forms.PointCloudForm()

  return render(request, 'main/form.html',
                {'title': 'Voxel Globe - Download',
                 'page_title': 'Voxel Globe - Download Point Cloud',
                 'form':form})

def cameras_krt(request):
  if request.method == 'POST':
    form = forms.TiePointForm(request.POST)
    if form.is_valid():
      from StringIO import StringIO
      import math
      import json
      import zipfile

      import numpy as np

      from voxel_globe.tools.camera import get_krt

      image_collection = form.cleaned_data['image_collection']

      _,_,_,origin = get_krt(image_collection.images.all()[0])
      krts = []
      name_format = 'frame_%%0%dd.txt' % int(math.ceil(math.log10(max(image_collection.images.all().values_list('id', flat=True)))))
      zip_s = StringIO()
      with zipfile.ZipFile(zip_s, 'w', zipfile.ZIP_DEFLATED) as zipper:
        for image in image_collection.images.all():
          k,r,t,_ = get_krt(image, origin=origin)
          krt_s = StringIO()
          np.savetxt(krt_s, np.array(k))
          krt_s.write('\n')
          np.savetxt(krt_s, np.array(r))
          krt_s.write('\n')
          np.savetxt(krt_s, np.array(t).T)
          zipper.writestr(name_format % image.id, krt_s.getvalue())
        zipper.writestr('scene.json', json.dumps({'origin':origin, 'longitude':origin[0], 'latitude':origin[1], 'altitude':origin[2]}))

      response = HttpResponse(zip_s.getvalue(), content_type='application/zip')
      response['Content-Length'] = len(response.content)
      response['Content-Disposition'] = 'attachment; ' + \
          'filename=cameras_%d.zip' % image_collection.id
      return response

  else:
    form = forms.TiePointForm()

  return render(request, 'main/form.html',
                {'title': 'Voxel Globe - Download',
                 'page_title': 'Voxel Globe - Download Cameras for Image Collection',
                 'form':form})

def image(request):
  if request.method == 'POST':
    form = forms.ImageForm(request.POST)
    if form.is_valid():
      image = form.cleaned_data['image']

      return redirect(image.originalImageUrl)
  else:
    form = forms.ImageForm()

  return render(request, 'main/form.html',
                {'title': 'Voxel Globe - Download',
                 'page_title': 'Voxel Globe - Download Image',
                 'form':form})