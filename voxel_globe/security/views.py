import os
from os import environ as env

from django.shortcuts import render, redirect, HttpResponse
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core import serializers

import voxel_globe.download.forms as forms

from voxel_globe.download.tools import xfilesend_response

from voxel_globe.websockets import ws_logger

import mimetypes

def images(request):
  #I'm not doing these "security" features, because I believe they will slow
  #everything down
  #1) Verify in /images directory
  #2) Take the path, extract the sha, and search the database for it. Now I can
  #   verify that the user has permission to access the file.
  #3) A better way to limit per user access?

  if os.path.isfile(request.path):
    filename = env['VIP_NGINX_XSENDFILE_PREFIX']+request.path
    return xfilesend_response(request, filename, disposition=None, 
        content_type=mimetypes.guess_type(request.path)[0])
  #Determining the mime type is not necessary to make ol3 viewer work

  if os.path.exists(request.path):
    raise PermissionDenied    
  
  raise Http404('File not found')
