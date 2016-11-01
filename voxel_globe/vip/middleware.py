import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

class RequireLoginMiddleware(MiddlewareMixin):
  """
  Middleware component that wraps the login_required decorator around
  matching URL patterns. To use, add the class to MIDDLEWARE_CLASSES and
  define LOGIN_REQUIRED_URLS and LOGIN_REQUIRED_URLS_EXCEPTIONS in your
  settings.py. For example:
  ------
  LOGIN_REQUIRED_URLS = (
      r'/topsecret/(.*)$',
  )
  LOGIN_REQUIRED_URLS_EXCEPTIONS = (
      r'/topsecret/login(.*)$',
      r'/topsecret/logout(.*)$',
  )
  ------
  LOGIN_REQUIRED_URLS is where you define URL patterns; each pattern must
  be a valid regex.
  
  LOGIN_REQUIRED_URLS_EXCEPTIONS is, conversely, where you explicitly
  define any exceptions (like login and logout URLs).
  """
  def __init__(self, *arg, **kwargs):
    self.required = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS)
    self.exceptions = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)
    super(RequireLoginMiddleware, self).__init__(*arg, **kwargs)

  def process_view(self, request, view_func, view_args, view_kwargs):
    # No need to process URLs if user already logged in
    if request.user.is_authenticated():
      return None

    # An exception match should immediately return None
    for url in self.exceptions:
      if url.match(request.path):
          return None

    # Requests matching a restricted URL pattern are returned
    # wrapped with the login_required decorator
    for url in self.required:
      if url.match(request.path):
        return login_required(view_func)(request, *view_args, **view_kwargs)

    # Explicitly return None for all non-matching requests
    return None

class TerminalLoggingMiddleware(MiddlewareMixin):
  def process_response(self, request, response):
    from sys import stdout
    if stdout.isatty():
      for query in connection.queries :
        print "\033[1;31m[%s]\033[0m \033[1m%s\033[0m" % (query['time'], " ".join(query['sql'].split()))
    return response
