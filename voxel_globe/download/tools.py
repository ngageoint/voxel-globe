import os

from django.shortcuts import HttpResponse
from django.http.response import FileResponse
from django.utils.encoding import smart_str

def xfilesend_response(request, filename, disposition='attachment', 
                       download_name=None, 
                       content_type='application/octet-stream'):
  ''' xfilesend_response is a helper function to use xsendfile if available 

      The httpd.conf files should have SetEnv VIP_XSENDFILE 1 to indicate 
      XSendFile is enabled. This is only accessible via the request.environ,
      not the os environ [link](https://modwsgi.readthedocs.org/en/develop/user-guides/configuration-guidelines.html#application-configuration).
      
      Arguments
      ---------
      filename - Full path to the file where it exists on disk

      Optional Arguments
      ------------------
      disposition - Content-Disposition Value, see 
        [here](http://www.iana.org/assignments/cont-disp/cont-disp.xhtml).
        Default is attachment, but None will result in the field not being set
      download_name - The name the webbrowser will default to if saved. Default
        is None, indicating do not use this feature. An empty string '' will 
        indicate to use the basename of the filename instead. You can specify
        any string to set the default to that name
      content_type - The MIME type. Default is application/octet-stream. Using
        application/force-download is considered hackish and ill advised

  '''

  if request.environ.get('VIP_XSENDFILE', '0') == '1':
    response = HttpResponse(content_type=content_type)
    response['X-Sendfile'] = smart_str(filename)
  else:
    response = FileResponse(open(filename, 'rb'), content_type=content_type)
    response['Content-Length'] = os.stat(filename).st_size

  if disposition:
    response['Content-Disposition'] = disposition

    if download_name is not None:
      if download_name:
        response['Content-Disposition'] += '; filename="%s"' % download_name
      else:
        response['Content-Disposition'] += '; filename="%s"' % \
            os.path.basename(filename)

  return response
