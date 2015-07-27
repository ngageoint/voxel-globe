import os
import sys
if sys.version_info[0] == 2 and sys.version_info[1] < 7:
  #Add a compatibility dir for python versions younger than 2.7
  sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], 
                               'compat'))

from subprocess import call, Popen, PIPE, STDOUT
from os import environ as env
from distutils.dir_util import mkpath
from glob import glob

from vsi.tools.redirect import PopenRedirect, Logger as LoggerWrapper

import logging
logger = logging.getLogger(__name__)

def shlex_join(args):
  import pipes
  args = map(pipes.quote, args)
  return ' '.join(args)

packageList = [
  'proj',
  'python',
#'py','pytest',
  'setuptools', 'pip', 'nose',

  'lcms', 'lcms2', 
  'openjpeg',
  'geos',
  'jsonc',
  'gmp',
  'mpfr',
  #'lapack',
  'atlas',
  'fftw',
  'pillow',

  'wxwidgets', 'wxpython',

  'numpy',
  'scipy',
  'pandas',
  'sympy',

  'six',
  'dateutil',
  'pytz',
  'backports_ssl',
  'certifi',
  'tornado',
  'pyparsing',
  'matplotlib',

  'zeromq',
  'pyzmq',
  'markupsafe',
  'jinja2',
  'jsonschema',
  'terminado',
  'ptyprocess',
  'sphinx_rtd_theme', 'snowballstemmer', 'docutils', 'babel', 'alabaster', 
                      'sphinx',
  'pygments',
  'pexpect',
  'ipython',

  'flask',
  'redis',
  'redis-py',
  'requests',
  'werkzeug',
  'itsdangerous',
  'greenlet',
  'pyyaml',
  'pystache', 'markdown', 'gevent', 'websocket', 'gevent-websocket',
  'bokeh',

  'tifffile',

  'utm',

  'rpdb',
  'winpdb',

  'opencv',

  'django',
  'djangorestframework',
  'djangorestframework_gis',
  'djangofilter',
  'django-model-utils',

  'rabbitmq',
  'httplib2',
  'pyrabbit',

  'anyjson',
  'amqp',
  'billiard',
  'kombu',
  'celery',
  'futures',
  'flower',

  'uuid',
  'postgresql',
  'pgadmin',
  'psycopg',

  'apr',
  'aprutil',
  'pcre',

  'gdal',

  'boost',
  'cgal',
  'sfcgal',

  'postgis',

  'httpd',
  'wsgi',

  'libgsf',
  'vips',

  'py',
  'colorama',
  'pytest',
  'mako',
  'decorator',
  'pytools',
  'appdirs',
  'pyopencl',

  'pba',
  'devil',
  'siftgpu',
  'pmvs2',
  'graclus',
  'cmvs',
  'visualsfm',

  'geographiclib']

class Rpm(object):
  def __init__(self, rpm_dir, rpm_command, rpmbuild_command, dry_run,
               rpm_db_path, check_dependencies, build_srpms, prefix, **opts):
    self.rpm_dir = rpm_dir
    self.rpm_command = rpm_command
    self.rpmbuild_command = rpmbuild_command
    self.dry_run = dry_run
    self.db_path = rpm_db_path
    self.check_dependencies = check_dependencies
    self.build_srpms=build_srpms
    self.prefix = prefix

  def specfile_from_name(self, specfile):
    ''' Takes a name or specfile name,and returns path specfile 
    
        example, 
        >>> specfile_from_name('python')
        /mydir/SPECS/python.spec
        >>> specfile_from_name('/mydir/SPECS/python.spec')
        /mydir/SPECS/python.spec
        >>> specfile_from_name('/mydir/SPECS/python')
        /mydir/SPECS/python.spec
        '''
    if not os.path.exists(specfile):
      specfile = os.path.join(self.rpm_dir, 'SPECS', specfile)
      if not os.path.exists(specfile):
        specfile = os.path.extsep.join([specfile, 'spec'])
    return specfile
    
  def call(self, command, args=[], capture_output=False, Popen=Popen):
    ''' Output is either captured or logged '''
    command = [command, '-v']
  
    if self.dry_run:
      def Popen(cmd, *args, **kwargs):
        logger.fatal(shlex_join(cmd))
        def communicate(input=None):
          return ('','')
        return type('Foo', (object,),{'wait':lambda x:None, 
                                      'communicate':communicate})()
  
    command += ['--dbpath', self.db_path]
    
    command += ['--define', '_topdir '+self.rpm_dir]
    
    command += args

    logger.debug('Calling: %s', shlex_join(command))

    if capture_output:
      pid = Popen(command, stdout=PIPE, stderr=PIPE)
      (stdout, stderr) = pid.communicate()
      if stdout:
        logger.debug(stdout)
      if stderr:
        logger.error(stderr)
      return (stdout, stderr, pid.wait())
    else:
      with PopenRedirect(LoggerWrapper(logger, logging.DEBUG)) as output:
        pid = Popen(command, stdout=output.stdout, stderr=STDOUT)
        return pid.wait()

  def rpm(self, args):
    rv = self.call(self.rpm_command, args)
    if rv:
      logger.fatal('rpm failed: '+str(args))
      raise Exception('rpm failed. Check DEBUG log file for details')
    return rv
    
  def rpmbuild(self, args):
    if not self.check_dependencies:
      args = args + ['--nodeps']
      
    rv = self.call(self.rpmbuild_command, args)
    if rv:
      logger.fatal('rpmbuild failed: '+str(args))
      raise Exception('rpmbuild failed. Check DEBUG file for details')
    return rv 

  def query(self, args):
    args = ['-q']+ args
    return self.call(self.rpm_command, args, capture_output=True)
  
  def build(self, args):
    if self.build_srpms:
      args = ['-ba'] + args
    else:
      args = ['-bb'] + args
    return self.rpmbuild(args)
  
  def is_installed(self, rpm):
    ''' Returns true if installed, else false '''
    args = ['--quiet', rpm]
    #Return if return value is 0
    return self.query(args)[2] == 0
  
  def erase(self, rpms):
    ''' Uninstall package by rpm name ''' 
    args = ['-e'] + rpms
    #Based on how rpm is designed, I decided to duplicated this if for erase 
    #and install
    if not self.check_dependencies: 
      args = ['--nodeps'] + args
    return self.rpm(args)
  
  def erase_spec(self, specfile):
    specfile = self.specfile_from_name(specfile)
    rpms = self.list_rpms_from_spec(specfile)
    self.erase(rpms)
  
  def smart_erase_spec(self, specfile):
    ''' Check if its installed first ''' 
    specfile = self.specfile_from_name(specfile)
    rpms = self.list_rpms_from_spec(specfile)
    for rpm in rpms:
      if self.is_installed(rpm):
        self.erase([rpm])

  def install(self, rpms):
    args = ['--prefix', self.prefix, '-hi']+ rpms
    #Based on how rpm is designed, I decided to duplicated this if for erase 
    #and install
    if not self.check_dependencies:
      args = ['--nodeps'] + args
    return self.rpm(args)

  def install_spec(self, specfile):
    specfile = self.specfile_from_name(specfile)
    rpms = self.list_rpm_filenames_from_spec(specfile)
    self.install(rpms)

  def smart_install_spec(self, specfile):
    ''' Remove then uninstall '''
    specfile = self.specfile_from_name(specfile)
    self.smart_erase_spec(specfile)
    self.install_spec(specfile)

  def list_full_rpms_from_spec(self, specfilename):
    args = ['--specfile', specfilename]
    stdout = self.query(args)[0]
    return stdout.splitlines()
  
  def list_rpm_filenames_from_spec(self, specfilename):
    args = ['--specfile', specfilename]
    args += ['--qf', os.path.join(self.rpm_dir, 'RPMS', '%{ARCH}', 
             '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}.rpm\\n')]
    #As far as I know, I have to manually put these together to make the full 
    #filename
    stdout = self.query(args)[0]
    return stdout.splitlines()
  
  def list_rpms_from_spec(self, specfilename):
    #Just rpm name, no version. Useful for rpm erase
    args = ['--specfile', specfilename]
    args += ['--qf', '%{NAME}\\n']
    #As far as I know, I have to manually put these together to make the full 
    #filename
    stdout = self.query(args)[0]
    return stdout.splitlines()
  
  def rebuild_db(self):
    logger.info('Rebuilding RPM Database')
    args = ['--rebuilddb']
    self.rpm(args)

def atlas_check():
  import multiprocessing as mp

  passed = True
    
  for cpu in range(mp.cpu_count()):
    with open('/sys/devices/system/cpu/cpu%d/cpufreq/scaling_governor' % cpu, 'r') as fid:
      if  not 'performance' in fid.read():
        logger.warning('CPU %s is NOT in performance mode. This prevents ATLAS optimization and will cause the ATLAS build to fail!', cpu)
        logger.warning('Enter the following as root');
        logger.warning("sudo bash -c 'cpu=0; while [ $cpu -lt $(nproc) ]; do echo performance > /sys/devices/system/cpu/cpu${cpu}/cpufreq/scaling_governor; let cpu=cpu+1; done'")
        passed=False
  return passed


def populate_roam():
  mkpath(env['VIP_ROAM_DIR'], 0755)
  roam_file = os.path.join(env['VIP_ROAM_DIR'], 'roam')
  with open(roam_file, 'w') as fid:
    fid.write('''#!/bin/bash
BASE_DIR=$(dirname ${BASH_SOURCE[0]})/..
BASE_DIR=$(cd ${BASE_DIR}; pwd)
export PATH=${BASE_DIR}%s:${PATH}
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${BASE_DIR}%s
#export LD_PRELOAD=${LD_LIBRARY_PATH}:${BASE_DIR}%s2
if [ "${BASH_SOURCE[0]}" == "$0" ]; then
  exec ${BASE_DIR}%s/$(basename $0) "${@}"
else
  source ${BASE_DIR}%s/$(basename ${BASH_SOURCE[0]}) "${@}"
fi''' % (env['VIP_BINDIR_BASE'],
         env['VIP_LIBDIR_BASE'],
         env['VIP_LIBDIR_BASE'],
         env['VIP_BINDIR_BASE'],
         env['VIP_BINDIR_BASE'],))
  
  os.chmod(roam_file, 0755)
  
  for file in glob(os.path.join(env['VIP_BINDIR'], '*')):
    roamee = os.path.join(env['VIP_ROAM_DIR'], os.path.split(file)[1])
    if not os.path.exists(roamee):
      os.link(roam_file, roamee)

def python_compile(prefix):
  import compileall
  import re
  compileall.compile_dir(prefix, force=1, quiet=1, 
      rx=re.compile('/roam/|/test/bad.*\.py|py3_test_grammar.py'))

def other():
  if not os.path.exists(env['VIP_LOCAL_SETTINGS']):
    with open(env['VIP_LOCAL_SETTINGS'], 'w') as fid:
      fid.writeline('#Put local setting in this file')
      
  with open(env['VIP_BASE_SCRIPT'], 'w') as fid:
    fid.write('''#!/bin/false
#DO NOT EDIT THIS AUTO GENERATED FILE! Edit %s instead
source ''' + os.path.join('$(dirname ${BASH_SOURCE[0]})', 
                          os.path.relpath(env['VIP_INSTALL_DIR'], 
                                          env['VIP_PROJECT_ROOT']),
                          'env.bsh'))

  new_file = os.path.join(env['VIP_DJANGO_PROJ_LIB'], 'egm96_15.gtx')
  if not os.path.exists(new_file):
    os.symlink(os.path.join(env['VIP_EXTERNAL_DATA_DIR'], 'egm96_15.gtx'),
               new_file)

def main(args=None, setupLogging=True, packageList=packageList):
  import argparse

  if setupLogging:
    sh = logging.StreamHandler()
    fh = logging.FileHandler(os.path.join(env.get('VIP_LOG_DIR', '.'), 'build.log'))
    sh.setLevel(logging.INFO)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
  else:
    if not logger.handlers:
      #Suppress any "no handler available" message
      logger.addHandler(logging.NullHandler())
  
  parser = argparse.ArgumentParser()
  aa = parser.add_argument

  #Commands
  aa('--erase', '-e', nargs='+', 
     help='''List of packges to uninstall. Does not build afterwards 
             (unless overridden)''')
  aa('--erase-all', default=False, action='store_true', 
     help='''Uninstall all (filtered) packages. Does not build afterwards 
             (unless overridden)''')
  aa('--compile-python-only', default=False, action='store_true',
     help='Compile .py only. Does not build afterwards (unless overridden)')
  aa('--populate-roam-only', default=False, action='store_true', 
     help='''Populate Roam Directory. Does not build afterwards (unless 
             overridden)''')
  aa('--list', '-l', default=False, action='store_true', 
     help='''List all available packages. Does not build afterwards (unless 
             overridden)''')
  aa('--build-only', default=False, action='store_true', 
     help='Just build, do not erase and install')
  aa('--reinstall-only', default=False, action='store_true', 
     help='Just resinstall, do not build')
  aa('--list-rpms', default=False, action='store_true', 
     help='List installed RPMs')
  aa('--build-all', default=False, action='store_true', 
     help='''Override to build all (filtered) packages after tasks that 
             normally do not build all, like erase, etc...''')
  aa('--rpm', nargs=2, 
     help='''Execute a specific rpm command, short circuited. First argument is
             spec file, second argument is rpm stage. Does not build afterwards
             (unless overridden)''')

  #Filters
  aa('--build', '-b', nargs='+', 
     help='Filter: Build only these packages instead')
  aa('--skip', '-s', nargs='+', 
     help='Filter: Skip building these packages')
  aa('--resume', 
     help='''Filter: Skip all packages before specified package, and resume 
             building starting with said package''')

  #Parameters
  aa('--build-srpms', default=False, action='store_true', 
     help='Enable the generation of SRPMs')
  aa('--rpm-cmd', dest='rpm_command', default='rpm', 
     help='rpm command file path')
  aa('--rpmbuild-cmd', dest='rpmbuild_command', default='rpmbuild', 
     help='rpmbuild command file path')
  aa('--check-dependencies', default=False, action='store_true', 
     help='Enable dependecy checking, currently disabled')
  aa('--rpm-dir', default=env.get('VIP_SRC_DIR', './rpm'), 
     help='RPM top directory')
  aa('--rpm-db-path', default=env.get('VIP_RPMDB_DIR', './os'), 
     help='RPM top directory')
  aa('--prefix',default=env.get('VIP_INSTALL_DIR', '.'), 
     help='Install prefix dir')

  #Special
  aa('--dryrun', '-n', dest='dry_run', default=False, action='store_true', 
     help='''Don't acutally run commands, just log them (may be less then 
             complete since files will be missing)''')

  opts = parser.parse_args(args)

  logger.debug('Start %s', str(opts))

  rpm = Rpm(**vars(opts))
  
  if not os.path.exists(opts.rpm_db_path):
    rpm.rebuild_db()
  
  build_all=True
  
  if opts.list_rpms:
    print rpm.query(['-a'])[0]
    build_all=False
    
  if opts.rpm:
    rpm_stages = {'prep':'-bp',
                  'build':'-bc', 
                  'install':'-bi',
                  'files':'-bl',
                  'source':'-bs'}
    specfile = rpm.specfile_from_name(opts.rpm[0])
    args = ['--short-circuit', rpm_stages[opts.rpm[1]], specfile]
    rpm.rpmbuild(args)
    build_all=False

  if opts.compile_python_only:
    python_compile(opts.prefix)
    build_all=False
  
  if opts.populate_roam_only:
    populate_roam()
    build_all=False
  
  if opts.erase:
    erase = map(str.lower, opts.erase)
    rpm.erase(erase)
    #for e in erase:
    #  rpm_erase(opts, e)
    build_all=False

  if opts.resume:
    try:
      resume = packageList.index(opts.resume.lower())
      packageList=packageList[resume:]
    except ValueError:
      logger.warning('Error resuming at %s, not in package list', 
                     opts.resume.lower())
    
  if opts.build:
    buildList = map(str.lower, opts.build)
    packageList = filter(buildList.__contains__, packageList) #Maintain order
    logger.info("Building only %s", packageList)

  if opts.skip:
    skipList =  map(str.lower, opts.skip)
    for skip in skipList:
      try:
        packageList.remove(skip)
      except ValueError:
        logger.warning('Problem skipping %s, not in package list '+
                       '(or already skipped)', skip)

  if opts.erase_all:
    #rpm.erase(packageList)
    for package in packageList:
      if package == 'python':
        continue
      logger.info('Uninstalling %s', package)
      rpm.smart_erase_spec(package)
    logger.info('Removing python last...')
    rpm.smart_erase_spec('python')
    logger.info('Removed python!')
    build_all = False

  if opts.list:
    for package in packageList:
      print package 
    build_all=False

  # # # MAIN BUILD SECTION # # #
  if build_all or opts.build_all:
    if not opts.reinstall_only:
      try:
        if 'atlas' in packageList and not atlas_check():
          logger.debug('You CAN set environment variable '\
            'VIP_ATLAS_SKIP_THROTTLE_CHECK to 1 to disable throttle '\
            'checking... But this is a VERY bad idea. Just use the root '\
            'command!')
      except:
        logger.warning('Atlas check failed, probably no cpufreq. this is '\
                       'normal when running a VM')

    #The first known package to error because of this is PIL, but if I fix it 
    #here, I know it'll never show up again!
    #Bug Report https://github.com/travis-ci/travis-ci/issues/1748
    mkpath(os.path.join(os.path.expanduser('~'), '.python-eggs'), 0755)
    env['QA_RPATHS'] = '0xFFFF'
    #This disables the rpath checks for rpmbuild in rhel. Annoying, but useless
    #since I WRAP everything using LD_LIBRARY_PATH
    
    for package in packageList:
      specfile = rpm.specfile_from_name(package)
      if not opts.reinstall_only:
        logger.info('Building %s', package)
        rpm.build([specfile]) #Build
      else:
        logger.info('Reinstalling %s', package)
      
      if not opts.build_only:
        rpm.smart_install_spec(specfile) #install
        
        populate_roam()
    
    if not opts.build_only:
      logger.info('Executing other commands')
      other()

    logger.info('Build complete')

if __name__=='__main__':
  main()
