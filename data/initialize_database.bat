:; $(dirname $0)/../_wrap.bsh python -x $0 "${@}"; exit $? ;  ^
'''
@echo off
call %~dp0\..\wrap.bat python -x %~dp0%~nx0 %*

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause
goto :eof
'''

#!/usr/bin/env python

from os import environ as env;
from os.path import join as path_join
import os
import tempfile
from subprocess import Popen
import time
import psycopg2

from pprint import pprint
from django.contrib.gis.utils.ogrinspect import mapping
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from django.core import management
import django
import pickle

logStdOut = None;
logStdErr = None;

def runCommand(cmd, haltOnFail=False, cwd=None):
  #logStdOut.write('Running %s\n\n'%' '.join(cmd))
  #print ' '.join(cmd)
  returnCode = Popen(cmd, stdout=logStdOut, stderr=logStdErr, cwd=cwd).wait();
  if haltOnFail and returnCode:
    raise Exception('Run command failed [%d]: %s' % (returnCode, ' '.join(cmd)))
  return returnCode;

def pg_initdb():
  fid = tempfile.NamedTemporaryFile(mode='w', delete=False);
  fid.write(env['VIP_POSTGRESQL_PASSWORD']);
  fid.close();
  cmd = ['pg_ctl', 'initdb', 
         '-D', env['VIP_POSTGRESQL_DATABASE'],
         '-o', ' '.join(['--username', env['VIP_POSTGRESQL_USER'],
                         '--pwfile', fid.name,
                         '--auth', env['VIP_POSTGRESQL_AUTH'],
                         '--encoding', env['VIP_POSTGRESQL_ENCODING'],
                         '--locale', env['VIP_POSTGRESQL_LOCALE']])]
  runCommand(cmd, haltOnFail=False);
  os.remove(fid.name);

def pg_startdb():
  cmd=['pg_ctl', 'start', 
       '-D', env['VIP_POSTGRESQL_DATABASE'],
       '-o', env['VIP_POSTGRESQL_SERVER_CREDENTIALS']]
  runCommand(cmd, haltOnFail=True);

def pg_stopdb():
  cmd=['pg_ctl', 'stop', 
       '-D', env['VIP_POSTGRESQL_DATABASE'],
       '-m', 'fast',
       '-o', env['VIP_POSTGRESQL_CREDENTIALS']]
  runCommand(cmd, haltOnFail=False);

def pg_isready():
  cmd=['pg_isready', 
       '-d', 'postgres'] + env['VIP_POSTGRESQL_CREDENTIALS'].split(' ')
  return runCommand(cmd, haltOnFail=False);

def pg_createdb(databaseName, otherArgs=[]):
  cmd = ['createdb']
  cmd += env['VIP_POSTGRESQL_CREDENTIALS'].split(' ')
  cmd += ['-e', #Verbosity!
          '--encoding', env['VIP_POSTGRESQL_ENCODING']]
  cmd += otherArgs + [databaseName]
  runCommand(cmd, haltOnFail=False);
  
def pg_dropdb(databaseName):
    cmd = ['dropdb']
    cmd += env['VIP_POSTGRESQL_CREDENTIALS'].split(' ')
    cmd += ['-e', #Verbosity!
            databaseName]
    runCommand(cmd, haltOnFail=False);
    
def psql(databaseName, sqlCmd):
  cmd=['psql']
  cmd += env['VIP_POSTGRESQL_CREDENTIALS'].split(' ')
  cmd += ['-d', databaseName, '-c'] + [sqlCmd];
  return runCommand(cmd, haltOnFail=False);

def load_world_data():
  from vsi.tools.dir_util import TempDir
  from voxel_globe.world import models
  from zipfile import ZipFile
  from glob import glob

  with TempDir(cd=True, mkdtemp=True) as temp_dir:
    with ZipFile(env['VIP_DJANGO_REGRESSION_SHAPEFILE'], 'r') as zip_file:
      zip_file.extractall(temp_dir)

    world_shp = glob(os.path.join(temp_dir, '*.shp'))[0]
    #print world_shp, '\n'

    ds = DataSource(world_shp)

    geometryName = u'mpoly';

    if 1: #Completely optional
      from django.contrib.gis.utils.ogrinspect import _ogrinspect
      print >>logStdOut, 'Your class model SHOULD look like this:\n'
      print >>logStdOut, '\n'.join([s for s in _ogrinspect(ds, 'WorldBorder', geom_name=geometryName, layer_key=0, srid=4326, multi_geom=True)]);

    world_mapping = mapping(ds, multi_geom=True, geom_name=geometryName, layer_key=0);

    print >>logStdOut, 'Loading database using mapping:'
    pprint(world_mapping, stream=logStdOut)

    try:
      lm = LayerMapping(models.WorldBorder, world_shp, world_mapping,
                        transform=False, encoding='iso-8859-1');
      lm.save(strict=True, verbose=True, stream=logStdOut);
    except:
      print 'Failed to load mapping data. It probably already exists!'

    #Cleanup so that TempDir can delete the dir
    del(ds, world_mapping, lm)


def add_srid_entry(srid, proj4text, srtext=None, ref_sys_name=None,
                   auth_name='EPSG', auth_srid=None, database=None):
  from django.contrib.gis.gdal import SpatialReference
  from django.db import connections, DEFAULT_DB_ALIAS

  if not database:
    database = DEFAULT_DB_ALIAS
  connection = connections[database]

  if not hasattr(connection.ops, 'spatial_version'):
    raise Exception('The `add_srs_entry` utility only works '
                    'with spatial backends.')
  if connection.ops.oracle or connection.ops.mysql:
    raise Exception('This utility does not support the '
                    'Oracle or MySQL spatial backends.')

  SpatialRefSys = connection.ops.spatial_ref_sys()
  #Model access TO spatial_ref_Sys
  #Why not just do django.contrib.gis.models.SpatialRefSys? I don't know?


  # Initializing the keyword arguments dictionary for both PostGIS
  # and SpatiaLite.
  kwargs = {'srid': srid,
            'auth_name': auth_name,
            'auth_srid': auth_srid or srid,
            'proj4text': proj4text,
            }

  # Backend-specific fields for the SpatialRefSys model.
  srs_field_names = SpatialRefSys._meta.get_all_field_names()
  if 'srtext' in srs_field_names:
    kwargs['srtext'] = srtext
  if 'ref_sys_name' in srs_field_names:
    # Spatialite specific
    kwargs['ref_sys_name'] = ref_sys_name

  # Creating the spatial_ref_sys model.
  try:
    # Try getting via SRID only, because using all kwargs may
    # differ from exact wkt/proj in database.
    SpatialRefSys.objects.using(database).get(srid=kwargs['srid'])
  except SpatialRefSys.DoesNotExist:
    SpatialRefSys.objects.using(database).create(**kwargs)

if __name__=='__main__':
  logStdOut = open(path_join(env['VIP_LOG_DIR'], 'db_setup_out.log'), 'w');
  logStdErr = open(path_join(env['VIP_LOG_DIR'], 'db_setup_err.log'), 'w');
  
  if pg_isready()==0:
    print "Error: Postgresql server is alreay running. Please stop it before\n", \
          "       running database setup"
    exit(1);

  if env['VIP_INITIALIZE_DATABASE_CONFIRM']=='1':
    print 'Would you like to delete the following databases\n' \
          '  %s\n' % env['VIP_POSTGRESQL_DATABASE_NAME'], \
          '(No means you will attempt to recreate on top of the existing DB)'
    deleteDatabase = raw_input('Delete database if exists [Y/n]?:');
  else:
    deleteDatabase = 'Y';
  
  if len(deleteDatabase) and deleteDatabase[0]=='Y':
    deleteDatabase = True;
  else:
    deleteDatabase = False;
    
  print '********** Initilizing database **********'
  pg_initdb();

#createuser -P
#psql GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;

  print '********** Starting database **********'
  pg_startdb();
  
  print '********** Waiting for database to come up **********'
  while 1:
    if pg_isready() == 0:
      print 'Database ready!'
      break;
    print 'Waiting for database to come up...'
    time.sleep(1);
  
  if deleteDatabase:
    print '********** Deleting database %s **********' % env['VIP_POSTGRESQL_DATABASE_NAME']
    pg_dropdb(env['VIP_POSTGRESQL_DATABASE_NAME'])
  
  print '********** Creating postgis template **********'
  pg_createdb('template_postgis');
  psql('template_postgis', 'CREATE EXTENSION postgis;')
  psql('template_postgis', 'CREATE EXTENSION postgis_topology;')
  psql('template_postgis', 'CREATE EXTENSION fuzzystrmatch;')
  psql('template_postgis', 'CREATE EXTENSION postgis_tiger_geocoder;')

  # Enabling users to alter spatial tables. Do we want this?
  psql('template_postgis', "GRANT ALL ON geometry_columns TO PUBLIC;");
  psql('template_postgis', "GRANT ALL ON geography_columns TO PUBLIC;");
  psql('template_postgis', "GRANT ALL ON spatial_ref_sys TO PUBLIC;");

  #Make it a template
  psql('postgres', "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';");

  print '********** Creating database %s **********' % env['VIP_POSTGRESQL_DATABASE_NAME']
  pg_createdb(env['VIP_POSTGRESQL_DATABASE_NAME'], otherArgs=['-T', 'template_postgis'])

  django.setup(); #New in 1.7, need to load app registry yourself.
  
  print '********** Adding SRIDs **********'

  #egm96 = SpatialReference('+proj=latlong +ellps=WGS84 +geoidgrids=@egm96_15.gtx,null +no_defs')
  add_srid_entry(srid=7428, auth_name='VIP/spatialreference.org', ref_sys_name='EGM96',
                 proj4text='+proj=latlong +ellps=WGS84 +geoidgrids=@egm96_15.gtx,null +no_defs',
                 srtext='COMPD_CS["WGS84 + EGM96",'
                          'GEOGCS["WGS 84 (3D EGM geoid height)",'
                            'DATUM["WGS_84",'
                              'SPHEROID["WGS 84",6378137,298.257223563,'
                                'AUTHORITY["EPSG","7030"]],'
                              'AUTHORITY["EPSG","6326"]],'
                            'PRIMEM["Greenwich",0,'
                              'AUTHORITY["EPSG","8901"]],'
                            'UNIT["degree",0.0174532925199433,'
                              'AUTHORITY["EPSG","9122"]],'
                            'AXIS["Geodetic latitude",NORTH],'
                            'AXIS["Geodetic longitude",EAST],'
                            'AUTHORITY["EPSG","4329"]],'
                          'VERT_CS["EGM96",'
                            'VERT_DATUM["EGM96",2005,'
                              'EXTENSION["PROJ4_GRIDS","@egm95_15.gtx,null"]],'
                            'AXIS["Gravity-related height",UP,'
                              'AUTHORITY["EPSG","5773"]]]]')


  #Permissions problem AND it needs to go away ANYWAYS, no reason to fix
  #print '********** Purging previous migrations in %s **********' % env['VIP_POSTGRESQL_DATABASE_NAME']
  #for rootDir, dirs, files in os.walk(env['VIP_DJANGO_PROJECT']):
  #  if rootDir.endswith('migrations'):
  #    for filename in files:
  #      if filename.endswith('.pyc'):
  #        os.remove(path_join(rootDir, filename))
  #      if filename.endswith('.py') and filename[4] == '_':
  #        try:
  #          int(filename[0:4])
  #          os.remove(path_join(rootDir, filename))
  #        except:
  #          pass;

  print '********** Making new migrations for %s **********' % env['VIP_POSTGRESQL_DATABASE_NAME']
  management.call_command('makemigrations', interactive=False, stdout=logStdOut)
  print '********** Creating django tables in %s **********' % env['VIP_POSTGRESQL_DATABASE_NAME']
  management.call_command('migrate', interactive=False, stdout=logStdOut)
  #syncdb will become migrate in django 1.7

  print '********** Creating Djanjo Users **********'
  from django.contrib.auth.models import User as DjangoUser; 
  #Chicken egg again
  with open(env['VIP_DJANGO_PASSWD'], 'rb') as fid:
    shadow = pickle.load(fid)
    #pw = fid.readline().strip()
    #fid.close();
  for s in shadow:
    if s[2]:
      print 'Creating superuser: %s' % s[0]
      user = DjangoUser.objects.create_superuser(s[0], env['VIP_EMAIL'], 'changeme');
    else:
      print 'Creating user: %s' % s[0]
      user = DjangoUser.objects.create_user(s[0], env['VIP_EMAIL']);

    user.password = s[1];
    user.save();

  print '********** Populating database WorldBorder **********'
  load_world_data();
 
  print '********** Stopping database **********'
  pg_stopdb();

  print '********** Waiting for database to go down **********'
  while 1:
    if pg_isready() != 0:
      print 'Database DOOOOOooooooown!'
      break;
    print 'Waiting for database to go down...'
    time.sleep(1);

#  print "Don't forget you probably need to run web/deploy.bat|bsh after starting the services"
