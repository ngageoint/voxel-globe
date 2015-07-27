"""
Django settings for vip project.

Merged with 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os import path, environ as env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GEOS_LIBRARY_PATH=env['VIP_DJANGO_GEOS_LIBRARY_PATH'];
GDAL_LIBRARY_PATH=env['VIP_DJANGO_GDAL_LIBRARY_PATH'];
#This shoudl work in windows too?

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '20hiyp8-=0+oan+sa(r$xz#j83jr5*13*(j_(a)9q234cynf+&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env['VIP_DJANGO_DEBUG']=='1'

TEMPLATE_DEBUG = env['VIP_DJANGO_TEMPLATE_DEBUG']=='1'

ALLOWED_HOSTS = env['VIP_DJANGO_ALLOWED_HOSTS'];

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'django.contrib.gis',
    'voxel_globe.meta',
    'voxel_globe.world',
    'voxel_globe.main',
    'voxel_globe.tiepoint',
    'voxel_globe.ingest',
    'voxel_globe.task',
    'voxel_globe.voxel_viewer',
    'voxel_globe.order.visualsfm',
    'voxel_globe.order.build_voxel_world',
    'django.contrib.staticfiles',
) #Staticfiles MUST come last, or else it might skip some files
  #at collectstatic deploy time!!!! This is one of the rare times
  #order matters

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'voxel_globe.vip.middleware.RequireLoginMiddleware',
)

SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
#SECURE_SSL_REDIRECT=True

ROOT_URLCONF = 'voxel_globe.vip.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'voxel_globe.vip.wsgi.application'

SERIALIZATION_MODULES = { 'geojson' : 'voxel_globe.serializers.geojson' }

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    #Eventually, 'DjangoModelPermissions' may be good?
#    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',), I set this in the viewSet instead
#    'PAGINATE_BY': 10, Leave default as get all
    'PAGINATE_BY_PARAM': 'page_size',
}

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'geodjango',
        'USER': env['VIP_POSTGRESQL_USER'],
        'PASSWORD': '',
        'HOST': '127.0.0.1',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

###STATICFILES_DIRS = [os.path.join(env['VIP_PYTHON_DIR'], 'lib', 'site-packages', '']
STATICFILES_DIRS = [env['VIP_DJANGO_STATIC_COMMON']]

STATIC_URL = '/'+env['VIP_DJANGO_STATIC_URL_PATH']+'/';
STATIC_ROOT = env['VIP_DJANGO_STATIC_ROOT'];
MEDIA_ROOT = env['VIP_DJANGO_MEDIA_ROOT'];

LOGIN_REQUIRED_URLS = (r'/(.*)$',)

LOGIN_REQUIRED_URLS_EXCEPTIONS = (
  r'/login.html(.*)$',
  r'/admin(.*)$', #Admin already does its own thing, leave it alone, even though I don't have to
  r'/login(.*)$',
  r'/logout(.*)$',
)

LOGIN_URL = '/login'

INGEST_TASKS = ['voxel_globe.arducopter.tasks',
                'voxel_globe.jpg_exif.tasks',
                'voxel_globe.no_metadata.tasks']

CELERY_TASKS = ['voxel_globe.world.tasks',
                'voxel_globe.tiepoint.tasks',
                'voxel_globe.visualsfm.tasks',
                'voxel_globe.build_voxel_world.tasks',
                'voxel_globe.tests.tasks']

CELERYD_MAX_TASKS_PER_CHILD = 1 #I don't think this is used yet