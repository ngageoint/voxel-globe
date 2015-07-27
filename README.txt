Table of contents
-----------------
 -General checkout
 -Linux
 --Setup
 -Windows 
 --Short version
 --Upgrading
 --Setup
 ---Database
 --Removal
 --Running in Windows
 --Starting services
 --Stopping services
 --Checking services
 --Controlling Individual Services
 --Special Windows Notes - Problems and solutions for windows
 -Testing
 -FAQ

====================
= General Checkout =
====================

git clone https://github.com/ngageoint/voxel-globe

=========
= Linux =
=========

Linux Setup
-----------

Short version - Install
-----------------------
1) ./install.bat
2) ./daemon.bat all start (as root if you chose yes for setup)

===========
= WINDOWS =
===========

Short version - Install
-----------------------
1) ./install.bat
2) ./startAll.bat

Instructions
============

Instructions will be given graphically (usually double clicking a bat file when
possible). All graphical examples can be done command line.

Everything is designed to be run as unpriledged and requests UAC elevation when
needed. This will have (UAC) before hand, and will be the only time admin 
rights are needed.

Windows - Upgrading
-------------------
If there is a previous install, you need to first stop all running services. 
It's always a good idea to wipe the previous build, as many things are always 
changing. Simply deleted the extra directories in 
localrepo/external/bin_Windows_NT_x86_64/ This currently include:
 -Apache24
 -erlang
 -osgeo4w
 -postgresql
 -python
 -rabbitmq_server
(I find it faster to move these dirs into a temp dir, and delete that in the 
 background, while I continue onto better things in life than waiting)

Windows - Setup
---------------
1) Double click ./external/bin_Windows_NT_x86_64/build.bat
   -Wait while all the zip files are extracted, and python is precompiles
2) (UAC) Double click ./external/bin_Windows_NT_x86_64/setup.bat
   -Wait while Redistributables are installed, services are created, and

Windows Setting up the database
-------------------------------
To setup the database to a known regression configuration, run 
./data/initialize_database.bat If you ever run this again, saying Y will
erase the ENTIRE django database, while not saying Y will cause duplicate
entries. It's your choice.

Windows Removal
---------------
1) Stop services (See Windows Stopping Services)
2) (UAC) Double click ./external/bin_Windows_NT_x86_64/unsetup.bat
   -Services are removed and firewall rules are removes (All rules named NPR)

Running in Windows
------------------
In order to make everything run conviently in windows WITHOUT cluttering the 
Windows enivronment, everything is "wrapped" by wrap.bat. You can either 
double-click when the instructions say, or open a command prompt, and run
the commands. However, you should not try running programs in 
./external/bin_Windows_NT_x86_64/ because they need to be wrapped first. You
can either
  1) Double click (or run with no parameters) wrap.bat, and a command prompt
     ready to go opens up. From there paths are already setup, and most 
     executables can be run by simply typing in their name, for example:
       python.exe
     Will start python up.
  or
  2) From a command prompt, you can type ./wrap.bat python.exe, and everything
     is run under the appropriate enviornment, without affecting the prompt
     the command is run from

Windows - Starting Services
---------------------------
To start all services, simply double click ./start all.lnk

Windows - Stopping Services
---------------------------
To start all services, simply double click ./stop all.lnk

Windows - Checking Services
---------------------------
To start all services, simply double click ./status all.lnk
-Running means it is still running
-Ready means it is not running, but ready to run

Everything logs to ./logs

Windows - Controlling Individual Services
-----------------------------------------
You can use Task Scheduler (Not covered here)

./daemon.bat is the script that all services use. Run with no arguments for 
usage.

Current service names are:
	httpd flower celery rabbitmq postgresql notebook
        all is a special name, that triggers all services
Current service commands are:
	start stop restart status

To control a service
	./daemon.bat {command} {service_name}

Special Windows Notes
---------------------

To access psql, please use psql.bat to automatically set the code page, and 
connection parameters.

-http://www.postgresql.org/docs/9.3/static/app-psql.html (Notes for Windows 
 Users) states your command prompt should use font Lucida Console instead 
 becasuse of the ANSI Page, but this is not automatically set because the 
 results are permanent and affect every Conlose for the User.

-start/status/stop all links will not work if you have the environment mounted
 as a Network drive. This is an inherit limit in Windows (still). The only way
 around it is to 
    1) NOT put the any files needed by these serives on a network drive, 
    or 
    2) Create a unprivledged user account, change all the tasks to "Run only 
       when logged in" as that user. Note, this is less secure than running as
       the Windows NT Network account, which was designed just for this purpose


===========
= Testing =
===========

1) Start all daemons
2) Open Web Browser
3) Go to http://localhost:80 (or 8080 if running unprivledged in Linux)
   - Test out gui, it should be working now
4) Go to http://localhost:80/world
   - Should dump out environment
5) http://localhost:80/world/search
   - Should see search form
6) Enter something easy like 33 by 37.245
   - Should see results for Syria, most importantly the area should be 
     reported as 18378
7) http://localhost:80/admin/
   - Log in and view the databases
8) http://localhost:5555/
   - You should see one Worker
9) http://localhost:8888/
   - IPython Notebook (experimental, works local host ONLY right now)
10) https://localhost:443 (8443 if running unprivledged in Linux)
   - Same as Steps 3-7

=======
= FAQ =
=======

Q1) Why does it say
django.core.exceptions.ImproperlyConfigured: Cannot determine PostGIS version for \
database "geodjango". GeoDjango requires at least PostGIS version 1.3. Was the
database created from a spatial database template?

A1) This is a poorly conditioned error message that occurs when the database is
    not running when geodjango attempts to run. This most often occurs when a
    django model is loaded by python, and the database has not started yet.
