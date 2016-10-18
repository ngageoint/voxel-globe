"""
Django settings for vip project.

Merged with 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from __future__ import absolute_import

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os import path, environ as env
from ast import literal_eval
from kombu import Exchange, Queue

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
try:
  from .secret_key import SECRET_KEY
except ImportError:
  #replace with django.core.management.utils.get_random_secret_key when the NEW django comes out, it's in master now
  from django.utils.crypto import get_random_string
  with open(os.path.join(os.path.dirname(__file__), 'secret_key.py'), 'w') as fid:
    fid.write("SECRET_KEY='%s'\n" % get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'))
  from .secret_key import SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env['VIP_DJANGO_DEBUG']=='1'

ALLOWED_HOSTS = env['VIP_DJANGO_ALLOWED_HOSTS']

# Application definition

INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'rest_framework',
  'rest_framework_gis',
  'django.contrib.gis',
  'voxel_globe.meta',
  'voxel_globe.world',
  'voxel_globe.main',   
  'voxel_globe.tiepoint',
  'voxel_globe.ingest',
  'voxel_globe.task',
  'voxel_globe.voxel_viewer',
  'voxel_globe.filter_number_observations',
  'voxel_globe.height_map',
  'voxel_globe.generate_point_cloud',
  'voxel_globe.ingest.metadata',
  'voxel_globe.ingest.payload',
  'voxel_globe.ingest.controlpoint',
  'voxel_globe.tiepoint_registration',
  'voxel_globe.visualsfm',
  'voxel_globe.build_voxel_world',
  'voxel_globe.download',
  'voxel_globe.tests',
  'voxel_globe.quick',
  'voxel_globe.create_site',
  'voxel_globe.image_view',
  'voxel_globe.event_trigger',
  'voxel_globe.channel_test',
  'voxel_globe.websockets',
  'voxel_globe.security',
  'channels',
  'voxel_globe.maintenance',
  #Maintenance must come near the end, or else it may miss some database models
  'django.contrib.staticfiles',
] #Staticfiles MUST come last, or else it might skip some files
  #at collectstatic deploy time!!!! This is one of the rare times
  #order matters

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'voxel_globe.vip.middleware.RequireLoginMiddleware',
]

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
        'voxel_globe.security.context_processors.websocket_token',
      ],
      'debug': env['VIP_DJANGO_TEMPLATE_DEBUG']=='1',
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
    'HOST': env['VIP_POSTGRESQL_HOST'],
    'PORT': env['VIP_POSTGRESQL_PORT'],
  }
}

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
  {
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
  },
]

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_DIRS = [env['VIP_DJANGO_STATIC_COMMON']]

STATIC_URL = env['VIP_DJANGO_STATIC_URL_PATH']+'/'
STATIC_ROOT = env['VIP_DJANGO_STATIC_DIR']
MEDIA_ROOT = env['VIP_DJANGO_MEDIA_DIR']

##### RequireLoginMiddleware #####

LOGIN_REQUIRED_URLS = (r'/(.*)$',)

LOGIN_REQUIRED_URLS_EXCEPTIONS = (
  r'^/admin(.*)$', #Admin already does its own thing, leave it alone, even though I don't have to
  r'^/login(.*)$',
  r'^/logout(.*)$',
)

LOGIN_URL = '/login/'

##### Celery #####
CELERYD_MAX_TASKS_PER_CHILD = 1

CELERYD_CONCURRENCY = env['VIP_NUMBER_CORES'] #default is #num of cores
CELERYD_LOG_COLOR = True

CELERY_DEFAULT_QUEUE = env['VIP_CELERY_DEFAULT_QUEUE']

CELERY_QUEUES = list()

for queue, exchange, key in zip(literal_eval(env['VIP_CELERY_QUEUES']),
                                literal_eval(env['VIP_CELERY_EXCHANGES']),
                                literal_eval(env['VIP_CELERY_KEYS'])):
  CELERY_QUEUES.append(Queue(queue, Exchange(exchange), routing_key=key))

BROKER_URL = env['VIP_CELERY_BROKER_URL']
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_RESULT_PERSISTENT = True

CELERY_TASK_SERIALIZER='json'
CELERY_ACCEPT_CONTENT=['json']  # Ignore other content
CELERY_RESULT_SERIALIZER='json'

CELERY_SEND_EVENTS=True

CELERY_DISABLE_RATE_LIMITS = True

CELERY_TRACK_STARTED = True

CELERYD_NODES="worker"

##### Websockets #####

CHANNEL_LAYERS = {
  "default": {
    "BACKEND": "asgi_redis.RedisChannelLayer",
    "CONFIG": {
      "hosts": ['redis://%s:%s' % (env['VIP_DOCKER_REDIS_CONTAINER_NAME'], env['VIP_REDIS_PORT'])],
    },
    "ROUTING": "voxel_globe.vip.routing.channel_routing",
  },
}