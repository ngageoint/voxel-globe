"""
WSGI config for vip project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.data.pop('', None);
#Fix some weird error where the environment variable '' is SET to '::=::\\'
#and the os module can't handle this. It is my hope that fixing it here ONCE 
#will cover everything. The only downside is I can not call unsetenv because 
#that is what fails I hope any other pids that are called do not get this 
#bogus environment variable somehow... Seems to work.

os.environ["DJANGO_SETTINGS_MODULE"] = os.environ['VIP_DJANGO_SETTINGS_MODULE']

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
