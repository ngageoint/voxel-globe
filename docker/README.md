# Voxel Globe Docker #

## TL; DR ##

1. `git clone --recursive {voxel_globe repo}`
2. `cd {repo_directory}`
3. `./just build` #Optionally build docker images, else they will need to be pulled
4. `./just reset-volume` #Delete and create volumes needed
4. Windows users must run `./just windows-volume`
5. `./just vxl` #compile library. If it gets in an infinite "Re-running cmake" loop on mac/windows, restart docker. The VM time drifts sometimes. Also, due to limitation of docker beta, "Input/output errors" will occur unless you set NUMBER_OF_PROCESSORS to a lower number (4 out of 8 for example)

        NUMBER_OF_PROCESSORS=4 ./just vxl 

6. `./just network` #Set up the voxel_globe docker network, only needs to be done once
7. `./just setup` #Initialize database
8. `./just start` #Start daemons
9. Open to web browser to [https://localhost/](https://localhost/)

## Debug environment ##

To run Django's runserver, first add `VIP_DEBUG=1` to `local_vip.env` and then
run `./just start_manage 

## Fully automated install ##

Simply run something like 
`VIP_INITIALIZE_DATABASE_CONFIRM=0 ./just build reset-volume vxl network setup start`

## Mac OS X and Windows ##

There are currently permissions issues when mounting the voxel_globe source
directory directly into a docker, making it hard to modify source files on the
host and have them be the same files in the docker. Currently Mac and Windows
need to copy the source directory into a docker volume and work off of those.
Further more, the postgresql database, image and storage directories need to be
docker volumes too.

Do not attempt CUDA/NVIDIA OpenCL, it won't work. They will only use the AMD 
APP OpenCL SDK

## Just commands ##

The `./just` command is used to execute many features for setting up and 
deploying Voxel Globe. For example, `./just build`. 

Many commands can be chained together, such as `./just build volume start stop`. 

Certain commands can take specific optional arguments, such as `start postgresql`
and some commands capture the rest of the arguments and pass them along, such as
`psql`, additional commands can not be chained after these terminating commands.

*Service names* include `celery`, `flower`, `httpd`, `postgresql`, `rabbitmq`, and
optionally `notebook` if `VIP_DOCKER_USE_NOTEBOOK` is `1`

### Setup ###

- **build** - Builds the docker images. This is necessary when editing the dockerfiles. 
**Default:** build all images. 
**Additional arguments**: *service name*. 
~~*Linux:"* The version of CUDA running in the host will automatically be identified and 
installed in the docker (CUDA 5.5 to 7.5 currently supported). To override (or
if CUDA is not installed in the host) set the environment variable `CUDA_VERSION`~~

        CUDA_VERSION=7.0 ./just build
~~The NVIDIA drivers **MUST** be installed on the host and a compatible version 
of CUDA must be selected, but CUDA does not need to be installed in the host.~~

- **pull** - Instead of building the image, pulls the docker images from the repo.
This is the preferred method as long as you are not actively developing the 
docker images. Always pull all images.
- **push** - Pushes all the docker images to the repo. `docker login` is required
at least once on the computer to make this work.

- **reset-volume** - (Deletes if they exist and) creates volumes necessary for Voxel Globe. This includes creating and populating an nVidia driver volume (Linux only), a VXL volume for storing vxl object code, a and Rabbit MQ volume for storing MQ status and cookies. 
- **windows-volume** - (Deletes if they exist and) creates volumes necessary for Windows operations. Since windows file permissions and lack of symlinks are so troublesome, additional docker volumes are creates for the postgresql database, image and storage directories.

- **vxl** - Compiles vxl_src in the the vxl volume. This is done internally to
handle permissions, installation, incremental building, and multiple build types.
Setting `VIP_VXL_BUILD_TYPE`, etc... in local_vip.env will affect this build. And
will actually store multiple builds in the vxl build, accessible via `./just debug`
- **network** - Create a docker network for all the containers to communicate over
- **setup** - Wipes and initializes the postgresql database and unzips javascript
libraries to make ready for running

### Main Docker Functions ###

- **start** - Starts the services. 
**Default:** start all services in order
**Additional arguments:** *service name* to start specific services only
- **stop** - Gracefully stop the services.
**Default:** stop all services in order
**Additional arguments:** *service name* to stop specific services only
- **quick-restart** - Gracefully restart services as fast as possible. When possible,
the container is not restarted, only the service is reloaded. This is not 
sufficient when changing environment variables. 
**Default:** Restart all services in order. 
**Additional arguments:** *service name* to restart specific services only
- **restart** - Same as **quick-restart**, excepts always restarts container. 
Sufficient for reloading environment variable changes
- **wait** - Wait for docker based services to stop
**Default:** wait for all services in order
**Additional arguments:** *service name* to wait for just specific service
- **kill** - Forcefully kills all containers
- **clean** - Removes stopped containers that are still around.
**Default:** is to build all images. 
**Additional arguments**: *service name*

### Development ###

- **dev** - Runs typical Q&A tasks for development tasks, primarily make
migrations and migrate/syncdb for Django
- **manage** - Runs Django manage.py for voxel_globe project
**Additional arguments:** passed along to manage.py


### Debugging ###
- **debug** - Start a generic debian docker with access to all docker volumes
and directories. *Warning* you are root
- **enter** - Executes an additional interactive bash session in a running container.
This is a great way to enter a docker and look around.
**Default:** - Lists all running dockers and you choose which one to enter
**Additional arguments**: *service name*
- **log** - Cat the logs from all running and stopped containers. (A little buggy)
- **ps** - Runs `docker ps` on Voxel Globe containers
- **telnet** - Runs telnet. This is useful for connecting to python debug sessions.
**Additional arguments:** passed along to telnet, such as `vip-postgresql 4444`

### Database ###

- **psql** - Runs arbitrary psql command
**Additional arguments:** passed along to psql
- **psqli** - Runs arbitrary interactive psql session
**Additional arguments:** passed along to psql
- **pg_dump** - Dumps the Voxel Globe database to stdout
- **pg_restore** - (Drops the Voxel Globe database if it exists, and) create and 
load the new database from filename specified as the first argument. Additional 
commands can not be chained after **pg_restore**
