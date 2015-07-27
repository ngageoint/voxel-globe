REM Common file for windows and Linux. Keep it simple!
REM 1) No commands other than "if not defined VARIABLE_NAME set VARIABLE_NAME=...
REM 2) No complicated expansions, no :\=/, no %~dp0, etc...
REM 3) No " quotes, windows doesn't need them
REM 4) Used ; only when separating paths, because in Linux it'll become :
REM ### Basic Settings ###
if not defined VIP_PROJECT_NAME set VIP_PROJECT_NAME=voxel_globe
if not defined VIP_DAEMON_GROUP set VIP_DAEMON_GROUP=voxel_globe
if not defined VIP_BUILD set VIP_BUILD=%VIP_OS%_%VIP_ARCH%
if not defined VIP_EMAIL set VIP_EMAIL=email@example.com
if not defined VIP_AUTOSTART set VIP_AUTOSTART=0
if not defined VIP_SERVICES set VIP_SERVICES=postgresql rabbitmq celeryd flower httpd notebook
REM Do I want to automatically start services on boot?
if not defined VIP_DAEMON_TIMEOUT set VIP_DAEMON_TIMEOUT=20.0
REM How long should daemons be waited on when starting/stopping before it is
REM considered a failure and move on.
if not defined VIP_FIREWALL_RULE_NAME set VIP_FIREWALL_RULE_NAME=NP2R
if not defined VIP_DAEMON_POSTFIX set VIP_DAEMON_POSTFIX=vip_daemon

REM Debug flags
if not defined VIP_DEBUG set VIP_DEBUG=0
REM This flags should ONLY be used in the following lines. Please create a new
REM Debug flag every time you need it. VIP_DEBUG is just an easy way to disable
REM or enable them all at once.
if not defined VIP_DJANGO_DEBUG set VIP_DJANGO_DEBUG=%VIP_DEBUG%
if not defined VIP_DJANGO_TEMPLATE_DEBUG set VIP_DJANGO_TEMPLATE_DEBUG=%VIP_DEBUG%
if not defined VIP_CELERY_AUTORELOAD set VIP_CELERY_AUTORELOAD=%VIP_DEBUG%
if not defined VIP_CELERY_DJANGO_DEBUG set VIP_CELERY_DJANGO_DEBUG=0
REM Special flag to attempt to disable django debug when loaded by celery.
REM HOPEFULLY this allows the django server server by httpd to be in debug
REM mode while the django loaded in celery is not. This should prevent the
REM memory leak in celery while still making debugging bearable
if not defined VIP_HTTPD_DEBUG_INDEXES set VIP_HTTPD_DEBUG_INDEXES=%VIP_DEBUG%
if not defined VIP_TEMP_KEEP set VIP_TEMP_KEEP=0
REM This flag disables temp directory cleanup. It is useful when you want to
REM debug/inspect the contents of a temporary directory from a processing job
REM Only works with tasks that correctly use
REM    "with voxel_globe.tools.tempTaskDir.taskDir():"

if not defined VIP_INITIALIZE_DATABASE_CONFIRM set VIP_INITIALIZE_DATABASE_CONFIRM=1

REM ### DIR Settings ###
if not defined VIP_CONF_DIR set VIP_CONF_DIR=%VIP_PROJECT_ROOT%/conf
if not defined VIP_LOG_DIR set VIP_LOG_DIR=%VIP_PROJECT_ROOT%/logs
if not defined VIP_LOCK_DIR set VIP_LOCK_DIR=%VIP_LOCALSTATEDIR%/lock/subsys
REM Currently only Linux even uses the lock dir
if not defined VIP_DATABASE_DIR set VIP_DATABASE_DIR=%VIP_PROJECT_ROOT%/data
if not defined VIP_EXTERNAL_DATA_DIR set VIP_EXTERNAL_DATA_DIR=%VIP_PROJECT_ROOT%/external/data
if not defined VIP_STORAGE_DIR set VIP_TEMP_DIR=%VIP_PROJECT_ROOT%/storage
if not defined VIP_TEMP_DIR set VIP_TEMP_DIR=%VIP_PROJECT_ROOT%/tmp
if not defined VIP_CONSTANT_TEMP_DIR set VIP_CONSTANT_TEMP_DIR=0
REM Very useful for debugging. Everything dumped into VIP_TEMP_DIR directly, instead of a random dir inside 

REM ### Vxl Settings ###
if not defined VIP_VXL_BUILD_DIR set VIP_VXL_BUILD_DIR=%VIP_PROJECT_ROOT%/external/vxl
if not defined VIP_CMAKE set VIP_CMAKE=cmake
REM set VIP_CMAKE_PLATFORM=Visual Studio 11
REM For example:
REM set VIP_VXL_CMAKE_OPTIONS='"-D", "var:type=value"'
if not defined VIP_VXL_CMAKE_ENTRIES set VIP_VXL_CMAKE_ENTRIES='BUILD_VGUI=ON'
if not defined VIP_VXL_BUILD_TYPE set VIP_VXL_BUILD_TYPE=Release
if not defined VIP_VXL_SRC_DIR set VIP_VXL_SRC_DIR=%VIP_PROJECT_ROOT%/external/vxl_src
if not defined VIP_OPENCL_DEVICE set VIP_OPENCL_DEVICE=gpu0
if not defined VIP_OPENCL_VERSION set VIP_OPENCL_VERSION=1.1

REM Must be set in local env for GDAL and vxl if not nvidia default
REM set VIP_OPENCL_INCLUDE_PATH=/usr/local/cuda/include
REM set VIP_OPENCL_LIBRARY_PATH=/usr/local/cuda/lib64
REM set VIP_OPENCL_LIBRARY=OpenCl

REM Intel OpenCL
REM set VIP_OPENCL_INCLUDE_PATH=/opt/intel/opencl-1.2-sdk-5.0.0.62/
REM set VIP_OPENCL_LIBRARY_PATH=/opt/intel/opencl/lib64/
REM set VIP_OPENCL_LIBRARY_NAME=libOpenCL.so
REM set VIP_OPENCL_VERSION=1.2



REM ### Python settings ###
if not defined PYTHONSTARTUP set PYTHONSTARTUP=%VIP_CONF_DIR%/pythonrc.py
if not defined VIP_NOTEBOOK_PORT set VIP_NOTEBOOK_PORT=8888
if not defined VIP_NOTEBOOK_IP set VIP_NOTEBOOK_IP=0.0.0.0
if not defined VIP_NOTEBOOK_LOG_DIR set VIP_NOTEBOOK_LOG_DIR=%VIP_LOG_DIR%/notebook
if not defined VIP_NOTEBOOK_PID_DIR set VIP_NOTEBOOK_PID_DIR=%VIP_PID_DIR%/notebook
if not defined VIP_NOTEBOOK_LOCK_DIR set VIP_NOTEBOOK_LOCK_DIR=%VIP_LOCK_DIR%/notebook
if not defined VIP_NOTEBOOK_PROFILE_DIR set VIP_NOTEBOOK_PROFILE_DIR=%VIP_PROJECT_ROOT%/notebooks/profile
if not defined BOXM2_OPENCL_DIR set BOXM2_OPENCL_DIR=%VIP_VXL_SRC_DIR%/contrib/brl/bseg/boxm2/ocl/cl/
if not defined VOLM_DIR set VOLM_DIR=%VIP_VXL_SRC_DIR%/contrib/brl/bbas/volm
if not defined VIP_PYTHONPATH set VIP_PYTHONPATH=%VIP_PROJECT_ROOT%
REM for voxel_globe package

REM ### Django settings
if not defined VIP_DJANGO_PROJECT set VIP_DJANGO_PROJECT=%VIP_PROJECT_ROOT%/voxel_globe
REM I am adding the namespace voxel_globe to ALL web content, so this and celery_processors will eventual be merged into JUST VIP_PROJECT_ROOT, and that will be the only thing added to pythonpath in env.bat
if not defined VIP_DJANGO_SITE set VIP_DJANGO_SITE=%VIP_DJANGO_PROJECT%/vip
if not defined VIP_DJANGO_STATIC_ROOT set VIP_DJANGO_STATIC_ROOT=%VIP_PROJECT_ROOT%/static_deploy
if not defined VIP_DJANGO_SETTINGS_MODULE set VIP_DJANGO_SETTINGS_MODULE=voxel_globe.vip.settings
if not defined VIP_DJANGO_STATIC_URL_PATH set VIP_DJANGO_STATIC_URL_PATH=static
if not defined VIP_DJANGO_STATIC_COMMON set VIP_DJANGO_STATIC_COMMON=%VIP_DJANGO_PROJECT%/static_common
if not defined VIP_DJANGO_MEDIA_ROOT set VIP_DJANGO_MEDIA_ROOT=%VIP_DJANGO_PROJECT%/media_root
REM Note: Since environment variables are process-wide, this doesn't work when you
REM run multiple Django sites in the same process. This can happen with mod_wsgi.
REM To avoid this problem, use mod_wsgi’s daemon mode with each site in its own daemon
REM process, or override the value from the environment by enforcing 
REM os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings" in your wsgi.py.

if not defined VIP_DJANGO_REGRESSION_APP set VIP_DJANGO_REGRESSION_APP=world
if not defined VIP_DJANGO_REGRESSION_SHAPEFILE set VIP_DJANGO_REGRESSION_SHAPEFILE=%VIP_EXTERNAL_DATA_DIR%/TM_WORLD_BORDERS-0.3.zip
if not defined VIP_DJANGO_ADMIN_USER set VIP_DJANGO_ADMIN_USER=vip
if not defined VIP_DJANGO_PASSWD set VIP_DJANGO_PASSWD=%VIP_PROJECT_ROOT%/shadow/django
if not defined VIP_DJANGO_ALLOWED_HOSTS set VIP_DJANGO_ALLOWED_HOSTS=['*']

REM ### POSTGRESQL Settings ###
REM For connecting
if not defined VIP_POSTGRESQL_HOST set VIP_POSTGRESQL_HOST=localhost
if not defined VIP_POSTGRESQL_PORT set VIP_POSTGRESQL_PORT=5432
REM set VIP_POSTGRESQL_USER=vip_postgresql REM AEN Obviously I still don't understand this still
if not defined VIP_POSTGRESQL_USER set VIP_POSTGRESQL_USER=postgresql
if not defined VIP_POSTGRESQL_PASSWORD set VIP_POSTGRESQL_PASSWORD=changeme
REM TODO use pgpass instead
if not defined VIP_POSTGRESQL_DATABASE_NAME set VIP_POSTGRESQL_DATABASE_NAME=geodjango
if not defined VIP_POSTGRESQL_CREDENTIALS set VIP_POSTGRESQL_CREDENTIALS=-U %VIP_POSTGRESQL_USER% -h %VIP_POSTGRESQL_HOST% -p %VIP_POSTGRESQL_PORT%
if not defined VIP_POSTGRESQL_SERVER_CREDENTIALS set VIP_POSTGRESQL_SERVER_CREDENTIALS=-h %VIP_POSTGRESQL_HOST% -p %VIP_POSTGRESQL_PORT%

REM For setup
if not defined VIP_POSTGRESQL_DATABASE set VIP_POSTGRESQL_DATABASE=%VIP_DATABASE_DIR%/postgresql
if not defined VIP_POSTGRESQL_PID_DIR set VIP_POSTGRESQL_PID_DIR=%VIP_PID_DIR%/postgresql
if not defined VIP_POSTGRESQL_LOG_DIR set VIP_POSTGRESQL_LOG_DIR=%VIP_LOG_DIR%/postgresql
if not defined VIP_POSTGRESQL_LOG set VIP_POSTGRESQL_LOG=%VIP_POSTGRESQL_LOG_DIR%/pg.log
if not defined VIP_POSTGRESQL_LOCK_DIR set VIP_POSTGRESQL_LOCK_DIR=%VIP_LOCK_DIR%/postgresql
if not defined VIP_POSTGRESQL_DIR set VIP_POSTGRESQL_DIR=%VIP_INSTALL_DIR%/postgresql

if not defined VIP_POSTGRESQL_ENCODING set VIP_POSTGRESQL_ENCODING=UTF-8
if not defined VIP_POSTGRESQL_AUTH set VIP_POSTGRESQL_AUTH=trust
REM This is ok for current dev, but will soon be md5, unless for some reason YEARS down the road,
REM db-namespace is needed, in which case we will switch over to ssl connections only with password auth

REM ### Celery Settings ###
if not defined VIP_CELERY_DEFAULT_NODES set VIP_CELERY_DEFAULT_NODES=vip
if not defined VIP_CELERY_DAEMON_USER set VIP_CELERY_DAEMON_USER=vip_celery
if not defined VIP_CELERY_PROCESSORS set VIP_CELERY_PROCESSORS=%VIP_PROJECT_ROOT%
REM This is temporary, I will remove it once it has been merged with the voxel globe dir, and 
if not defined VIP_CELERY_PID_DIR set VIP_CELERY_PID_DIR=%VIP_PID_DIR%/celery
if not defined VIP_CELERY_LOG_DIR set VIP_CELERY_LOG_DIR=%VIP_LOG_DIR%/celery
if not defined VIP_CELERY_LOG_LEVEL set VIP_CELERY_LOG_LEVEL=INFO
if not defined VIP_CELERY_TASK_LOG_DIR set VIP_CELERY_TASK_LOG_DIR=%VIP_CELERY_LOG_DIR%
if not defined VIP_CELERY_LOCK_DIR set VIP_CELERY_LOCK_DIR=%VIP_LOCK_DIR%/celery
if not defined VIP_CELERY_APP set VIP_CELERY_APP=voxel_globe.tasks
if not defined VIP_CELERY_CONFIG_MODULE set VIP_CELERY_CONFIG_MODULE=voxel_globe.celeryconfig
if not defined VIP_CELERY_DBSTOP_IF_ERROR set VIP_CELERY_DBSTOP_IF_ERROR=0

if not defined VIP_FLOWER_HOST set VIP_FLOWER_HOST=localhost
if not defined VIP_FLOWER_PORT set VIP_FLOWER_PORT=5555

if not defined VIP_NOTEBOOK_RUN_DIR set VIP_NOTEBOOK_RUN_DIR=%VIP_CELERY_PROCESSORS%

REM ##### RABITMQ Settings ##### 
if not defined VIP_RABBITMQ_PID_DIR set VIP_RABBITMQ_PID_DIR=%VIP_PID_DIR%/rabbitmq
if not defined VIP_RABBITMQ_LOCK_DIR set VIP_RABBITMQ_LOCK_DIR=%VIP_LOCK_DIR%/rabbitmq
if not defined VIP_RABBITMQ_LOG_DIR set VIP_RABBITMQ_LOG_DIR=%VIP_LOG_DIR%/rabbitmq
if not defined VIP_RABBITMQ_PID_FILE set VIP_RABBITMQ_PID_FILE=%VIP_PID_DIR%/rabbitmq.pid

if not defined VIP_RABBITMQ_USER set VIP_RABBITMQ_USER=vip_rabbitmq
if not defined VIP_RABBITMQ_MNESIA_BASE set VIP_RABBITMQ_MNESIA_BASE=%VIP_DATABASE_DIR%

REM ##### Image Server Settings #####
if not defined VIP_IMAGE_SERVER_PROTOCOL set VIP_IMAGE_SERVER_PROTOCOL=http
if not defined VIP_IMAGE_SERVER_HOST set VIP_IMAGE_SERVER_HOST=localhost
if not defined VIP_IMAGE_SERVER_PORT set VIP_IMAGE_SERVER_PORT=80
if not defined VIP_IMAGE_SERVER_URL_PATH set VIP_IMAGE_SERVER_URL_PATH=images
  REM Where are the images served from
if not defined VIP_IMAGE_SERVER_ROOT set VIP_IMAGE_SERVER_ROOT=%VIP_PROJECT_ROOT%/images
  REM Where are the images physically/virtually?

REM ##### Apache HTTPD Settings ##### 
if not defined VIP_HTTPD_CONF set VIP_HTTPD_CONF=%VIP_CONF_DIR%/httpd.conf
if not defined VIP_HTTPD_PORT set VIP_HTTPD_PORT=80
if not defined VIP_HTTPD_SSL_PORT set VIP_HTTPD_SSL_PORT=443
if not defined VIP_HTTPD_DAEMON_USER set VIP_HTTPD_DAEMON_USER=vip_httpd
if not defined VIP_HTTPD_DAEMON_GROUP set VIP_HTTPD_DAEMON_GROUP=%VIP_DAEMON_GROUP%
if not defined VIP_HTTPD_PID_DIR set VIP_HTTPD_PID_DIR=%VIP_PID_DIR%/httpd
if not defined VIP_HTTPD_LOG_DIR set VIP_HTTPD_LOG_DIR=%VIP_LOG_DIR%/httpd
if not defined VIP_HTTPD_LOCK_DIR set VIP_HTTPD_LOCK_DIR=%VIP_LOCK_DIR%/httpd
if not defined VIP_HTTPD_LOG_LEVEL set VIP_HTTPD_LOG_LEVEL=info
if not defined VIP_HTTPD_DEPLOY_ON_START set VIP_HTTPD_DEPLOY_ON_START=1
if not defined VIP_HTTPD_SERVER_NAME set VIP_HTTPD_SERVER_NAME=www.example.com
if not defined VIP_HTTPD_SSL_CERT set VIP_HTTPD_SSL_CERT=%VIP_CONF_DIR%/server.crt
if not defined VIP_HTTPD_SSL_KEY set VIP_HTTPD_SSL_KEY=%VIP_CONF_DIR%/server.key

if not defined VIP_WSGI_PYTHON_DIR set VIP_WSGI_PYTHON_DIR=%VIP_PYTHON_DIR%
REM THIS was annoying, WSGI auto adds bin in linux, SO my roam isn't used, however
REM APACHE is started in my environment, so I'm sure this is why everything is working?
if not defined VIP_WSGI_PYTHON_PATH set VIP_WSGI_PYTHON_PATH=%VIP_DJANGO_PROJECT%;%VIP_CELERY_PROCESSORS%
REM For the initial wsgi.py file and all Celery processors
if not defined VIP_WSGI_SCRIPT_ALIAS set VIP_WSGI_SCRIPT_ALIAS=%VIP_DJANGO_SITE%/wsgi.py
if not defined VIP_WSGI_ACCESS_SCRIPT set VIP_WSGI_ACCESS_SCRIPT=%VIP_DJANGO_SITE%/auth.py

if not defined VIP_UTIL_DIR set VIP_UTIL_DIR=%VIP_INSTALL_DIR%/utils

if not defined VIP_VSI_DIR set VIP_VSI_DIR=%VIP_PROJECT_ROOT%/external/vsi

REM ADD this later, to add loops to firewall rules in linux setup/unsetup
if not defined VIP_TCP_PORTS set VIP_TCP_PORTS=""
if not defined VIP_UDP_PORTS set VIP_UDP_PORTS=""

REM *********** NON-VIP Section. There can affect ANYTHING ***********
REM These parameters are not protected by the VIP Prefix, and thus
REM Affect many application, but hopefully in a good way :)

if not defined DJANGO_SETTINGS_MODULE set DJANGO_SETTINGS_MODULE=%VIP_DJANGO_SETTINGS_MODULE%
if not defined CELERY_CONFIG_MODULE set CELERY_CONFIG_MODULE=%VIP_CELERY_CONFIG_MODULE%

REM I don't know if this is actually used, but it is mentioned in the Geodjango tutorial
if not defined PROJ_LIB set PROJ_LIB=%VIP_DJANGO_PROJ_LIB%
if not defined GDAL_DATA set GDAL_DATA=%VIP_DJANGO_GDAL_DATA%
if not defined POSTGIS_ENABLE_OUTDB_RASTERS set POSTGIS_ENABLE_OUTDB_RASTERS=1
if not defined POSTGIS_GDAL_ENABLED_DRIVERS set POSTGIS_GDAL_ENABLED_DRIVERS=ENABLE_ALL
if not defined POSTGIS_GDAL_ENABLED_DRIVERS set POSTGIS_GDAL_ENABLED_DRIVERS=GTiff PNG JPEG GIF XYZ
