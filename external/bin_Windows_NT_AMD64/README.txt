Windows binaries go here. They are compiled with Microsoft Visual Studio's 2008 Express edition, so you will need the Redistributable

Windows tried to install precompiled that are already build. The few that still have to be built are pull from src:
-tifffile - Python package
-utm - Python package
-Django - Python package
-(ipython? I don't care enough about this right now)

gdal-1.11.0_scripts.zip - I ripped the scripts out of http://www.gisinternals.com/sdk/PackageList.aspx?file=release-1600-x64-gdal-1-11-mapserver-6-4.zip
wxPython3.0-win64-3.0.0.0-py27 - I ripped the binaries out of http://downloads.sourceforge.net/wxpython/wxPython3.0-win64-3.0.0.0-py27.exe
tifffile-2014.02.05.zip - I put together the files from http://www.lfd.uci.edu/~gohlke/code/tifffile.py.html to make an install setup

rabbitmq_server.zip from http://www.rabbitmq.com/releases/rabbitmq-server/v3.3.1/rabbitmq-server-3.3.1.exe
erlang.zip from http://www.erlang.org/download/otp_win64_17.0.exe
