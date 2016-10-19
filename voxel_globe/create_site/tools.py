import requests
from requests.packages.urllib3.util.retry import Retry
import os
import urlparse
import sys
import time
import json
from contextlib import closing

#--------------------------------------------------
# PLANETLABS COMMUNICATION
#--------------------------------------------------
class PlanetClient():
    
    # authorization
    __KEY = None
    __AUTH = None
    
    # urls    
    _URL_BASE = "https://api.planet.com/v0/"
    
    _URL_SCENE = urlparse.urljoin(_URL_BASE,"scenes/")
    _URL_PLANETSCOPE = urlparse.urljoin(_URL_SCENE,"ortho/")
    _URL_RAPIDEYE = urlparse.urljoin(_URL_SCENE,"rapideye/")
    _URL_LANDSAT = urlparse.urljoin(_URL_SCENE,"landsat/")    
    
    # communication
    _SESSION = None
    
    
    # initialize
    def __init__(self,key=None):     

        # initialize session 
        self._SESSION = requests.Session()
        retries = Retry(total=5,backoff_factor=0.1,status_forcelist=[500,502,503,504])
        self._SESSION.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
        self._SESSION.timeout = 5 # seconds
        
        # store authorization
        self.setAuth(key)
    
    # enter & exit ("with")
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
        
        
    # additional authorization
    def setAuth(self,key = None):
        if not key or key is None:
            self.__KEY = None
            auth = None        
        else:
            self.__KEY = key
            auth = (key,'')            
        self._SESSION.auth = auth
        

    # check that authorization has been defined
    def isAuth(self):
        return (self.__KEY is not None)
        
    def checkAuth(self):
        if not self.isAuth: raise ValueError('Missing Authorization')  
    
    
    # query number of images
    def countImages(self,query={}):
        scenes,total = self.__queryImages(query=query,flag_images=False)
        return total

        
    # query image descriptions
    def describeImages(self,query={}):
        scenes,total = self.__queryImages(query=query,flag_images=True)
        return scenes
    
    
    # query imagery from restful interface
    def __queryImages(self,query={},flag_images=False):
    
        # confirm authorization
        self.checkAuth()
        
        # pagination parameter
        if flag_images:
            count = 100
        else:
            count = 1
        
        # get parameters
        params = {
            'order_by': 'acquired desc',
            'count': count,
            }
        
        # queries
        if 'aoi' in query:
            tmp = query['aoi']
            if isinstance(tmp, dict): tmp = json.dumps(tmp)            
            params['intersects'] = tmp
        if 'start' in query:
            params['acquired.gte'] = query['start'].isoformat()
        if 'stop' in query:
            params['acquired.lte'] = query['stop'].isoformat()
        if 'cloudmax' in query:
            params['cloud_cover.estimated.lte'] = query['cloudmax']
        
        # platform(s) to query
        if 'platforms' not in query:
            platforms = ['planetscope','rapideye']  
        else:
            platforms = query['platforms']
            if not isinstance(platforms,(list,tuple)): platforms = [platforms]

        # scene endpoints to query
        scene_urls = self.__platforms_to_endpoints(platforms)    

        # initialize outputs
        scenes = []
        total = 0
        
        # check all named platforms
        for url in scene_urls:                
            next_url = url    
            next_params = params
            
            # retreive paginated info     
            while next_url:
                
                # GET request
                response = self._SESSION.get(next_url,params=next_params)
                check_response(response)

                # JSON response
                data = response.json()
                
                # determine total number of images
                total = total + data['count']
                if not flag_images: break
                
                # add scenes to list & continue
                scenes.extend(data['features'])
                next_url = data["links"].get("next", None)
                next_params = None
        
        # cleanup
        return scenes, total
    
    
    # describe single image ID
    def describeID(self,id=None,platform=None):
    
        # confirm authorization
        self.checkAuth()
        
        # generate image data url
        self_url = self.__platforms_to_endpoints([platform])
        self_url = urlparse.urljoin(self_url[0],id)
            
        # GET request
        response = self._SESSION.get(self_url)
        check_response(response)

        # cleanup
        data = response.json()
        return data['features']

    
    # download thumbnails
    def downloadThumbnails(self,scenes,type='unrectified',
        size='md',format='png',folder=None):
        
        # confirm authorization
        self.checkAuth()
        
        # check inputs
        if not isinstance(scenes,(list,tuple)): scenes = [scenes]        
        
        format = format.lower()
        if format not in ['png','jpg','jpeg']:
            raise ValueError('Invalid thumbnail format <%s>'%format)
        
        size = size.lower()
        if size not in ['sm','md','lg']:
            raise ValueError('Invalid thumbnail size <%s>'%size)
        
        type = type.lower()
        if type == 'unrectified':
            thumb = 'square_thumbnail'
        else:
            thumb = 'thumbnail'
        
        # gather info for download
        urls = [s['properties']['links'][thumb] for s in scenes]
        params = {"size":size,"format":format}
        
        # download thumbnails
        return self.__download(urls,params=params,folder=folder)
        
    
    # download images
    def downloadImages(self,scenes,type='unrectified.zip',folder=None):
        
        # confirm authorization
        self.checkAuth()
        
        # check inputs
        if not isinstance(scenes,(list,tuple)): scenes = [scenes]  
        
        if type == 'unrectified.zip':
            keys = ['unrectified','zip']
        elif type == 'unrectified':
            keys = ['unrectified','full']
        elif type == 'analytic':
            keys = ['analytic','full']
        elif type == 'visual':
            keys = ['visual','full']
        else:
            raise ValueError('Unrecognized type <%s>'%type)

        # gather URLs for download
        urls = []
        for scene in scenes:
            tmp = scene['properties']['data']['products']
            for k in keys: tmp = tmp[k]
            urls.append(tmp)

        # download images
        return self.__download(urls,folder=folder)
        
    
    # download any link    
    def __download(self,urls,params=None,folder=None):
    
        # check folder
        if folder is None:
            folder = os.getcwd()
        elif not os.path.isdir(folder):
            raise IOError('Directory missing <%s>'%folder)

        # initialize output
        files = []
            
        # download data from URL to file
        for url in urls:
        
            with closing(self._SESSION.get(url,params=params,stream=True)) as r:                
                check_response(r)
            
                file = r.headers['content-disposition'] \
                    .split("filename=")[-1].strip("'\"")
                file = os.path.join(folder,file)             
                                
                with open(file,'wb') as fid:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk: # filter out keep-alive new chunks
                            fid.write(chunk)
                            fid.flush()

                files.append(file)
            
        return files
    
        
    # discover appropriate scene endpoint
    def __platforms_to_endpoints(self,platforms):
       
        # initialize output
        urls = []
        
        # translate platform urls
        for platform in platforms:
            platform = platform.lower()        
        
            if platform == 'planetscope':
                url = self._URL_PLANETSCOPE
            elif platform == 'rapideye':
                url = self._URL_RAPIDEYE
            elif platform == 'landsat':
                url = self._URL_LANDSAT 
            else:
                print platforms
                raise ValueError('unrecognized platform <%s>',platform)    
    
            urls.append(url)
            
        return urls
        

        
# HELPER: check response
# https://www.planet.com/docs/v0/general-concepts/#errors
def check_response(response):
    try:
        response.raise_for_status()         
        
    except requests.exceptions.HTTPError:
        print('******************************')
        print('ERROR: API get request failed')
        print response
        print response.text
        if response.status_code == 400:
            try: 
                print json.dumps(response.json(), indent=2)
            except:
                pass
        print('******************************')
        raise   

            