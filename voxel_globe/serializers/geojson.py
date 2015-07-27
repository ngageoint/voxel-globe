'''This was based off a snippet, but it was so broeken, I had to start over'''

from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers.json import Serializer as OverloadedSerializer
from django.core.serializers.json import Deserializer
#from wadofstuff.django.serializers.python import Serializer as OverloadedSerializer
import json
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.core.serializers.python import Deserializer as PythonDeserializer
from StringIO import StringIO
class Serializer(OverloadedSerializer):
    def handle_field(self, obj, field):
        """
        If field is of GeometryField than encode otherwise call parent's method
        """
        value = field._get_val_from_obj(obj)
        if isinstance(field, GeometryField):
            self._current[field.name] = value
        else:
            super(Serializer, self).handle_field(obj, field)


    def end_object(self, obj):
        # self._current has the field data
        indent = self.options.get("indent")
        if not self.first:
            self.stream.write(",")
            if not indent:
                self.stream.write(" ")
        if indent:
            self.stream.write("\n")
        json.dump(self.get_dump_object(obj), self.stream,
                  cls=DjangoGEOJSONEncoder, **self.json_kwargs)
        self._current = None
    

class DjangoGEOJSONEncoder(DjangoJSONEncoder):
    """
    DjangoGEOJSONEncoder subclass that knows how to encode GEOSGeometry value
    """
    
    def default(self, o):
        """ overload the default method to process any GEOSGeometry objects otherwise call original method """ 
        if isinstance(o, GEOSGeometry):
            #return o.geojson
            dictval = json.loads(o.geojson)
            #raise Exception(o.ewkt)
###            dictval['__GEOSGeometry__'] = ['__init__', [o.ewkt]] #json class hint; see http://json-rpc.org/wiki/specification
#Necessary to desearialize, and I don't currently CARE
            return dictval
        else:
            return super(DjangoGEOJSONEncoder, self).default(o)


'''def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    if not isinstance(stream_or_string, (bytes, six.string_types)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode('utf-8')
    try:
        objects = json.loads(stream_or_string)
        for obj in PythonDeserializer(objects, **options):
            yield obj
    except GeneratorExit:
        raise
    except Exception as e:
        # Map to deserializer error
        six.reraise(DeserializationError, DeserializationError(e), sys.exc_info()[2])'''

def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    def GEOJsonToEWKT(dict):
        """ 
        Convert to a string that GEOSGeometry class constructor can accept. 
         
        The default decoder would pass our geo dict object to the constructor which 
        would result in a TypeError; using the below hook we are forcing it into a 
        ewkt format. This is accomplished with a class hint as per JSON-RPC 
        """ 
        if '__GEOSGeometry__' in dict: # using class hint catch a GEOSGeometry definition 
            return dict['__GEOSGeometry__'][1][0]
         
        return dict
    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    for obj in PythonDeserializer(json.load(stream, object_hook=GEOJsonToEWKT), **options):
        yield obj