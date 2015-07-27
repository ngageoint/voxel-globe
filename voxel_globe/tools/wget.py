import urllib2
import Cookie

from StringIO import StringIO
import zlib

def authorizeBasic(user=None, password=None, realm=None, uri=None):
  #This was needed. But not anymore
  if user and password and realm and uri:
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm=realm, uri=uri, user=user, passwd=password)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)

def _makeCookieString(cookie):
  simpleCookie = Cookie.SimpleCookie(cookie)
  cookieString = []
  for morselName in simpleCookie:
    cookieString.append('%s=%s' % (morselName, simpleCookie[morselName].coded_value))
  return '; '.join(cookieString)

def _getSecretKey():
  '''Django specific function to get a cookie dictionary with the secret key in
     it already, to ease trusted download'''
  from django.conf import settings
  return settings.SECRET_KEY

def download(url, filename, chunkSize=2**20, cookie={}, secret=False):
  #start simple, add feautres as time evolves
  #cookie - an optional dictionary
  #secret - django specific to load django settings file (based off of 
  #         os.environ['DJANGO_SETTINGS'] of course), and overwrite
  #         cookie 'secretkey' with the encoded values

  if secret:
    cookie['secretkey'] = _getSecretKey();

  request = urllib2.Request(url);
  request.add_header('Accept-encoding', 'gzip');
  if cookie:
    request.add_header('Cookie', _makeCookieString(cookie))
  context=None
  if url.startswith('https://'):
    import ssl
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
  response = urllib2.urlopen(request, context=context);
  if response.info().get('Content-Encoding') == 'gzip':
    gzipped = True;
    decompressor = zlib.decompressobj(16+zlib.MAX_WBITS)
    #Why 16+zlib.MAX_WBITS???
    #http://www.zlib.net/manual.html
    #Basically means gzip for zlib
  else:
    gzipped = False;

  with open(filename, 'wb') as output:
    buf = 'do';
    while buf:
      buf = response.read(chunkSize);
      if gzipped:
        output.write(decompressor.decompress(buf))
      else:
        output.write(buf);
