# Voxel Globe Docker #

###Overview
Calibrates aerial camera models and constructs 3D models from video sequences as well applications for 3D models such as change detection. 

## TL; DR ##

1. `git clone --recursive {voxel_globe repo}` See [cloning](#cloning)
2. `cd {repo_directory}`
3. `./just pull` #Optionally build docker images instead
4. `./just reset-volume` #Delete and create volumes needed
4. Windows users must run `./just windows-volume`
5. `./just vxl` #compile library. **WARNING** If it gets in an infinite "Re-running cmake" loop on mac/windows, restart docker. The VM time drifts sometimes when in sleep mode.
6. `./just network` #Set up the voxel_globe docker network, only needs to be done once
7. `./just setup` #Initialize database
8. `./just start` #Start daemons
9. Open to web browser to [https://localhost/](https://localhost/) on Linux or [https://docker.local/](https://docker.local/) on Mac or [https://docker/](https://docker/) on Windows

## Cloning ##

All submodules all added via their https url. If you need to use the ssh protocol
instead, the submodules can be switched over to their ssh urls. Instead of step
1 above, run:

1. `git clone {voxel_globe repo}`
2. `sed -r 's| url(.*)https://([^/]*)/| url\1git@\2:|' -i .gitmodules`
3. `git submodule sync`
4. `git submodule init`
4. `git checkout .gitmodules`
5. `git submodule update`

**NOTE**: A faster clone can also be achieved by `GIT_LFS_SKIP_SMUDGE=1 git clone ...`
followed by `git lfs pull`

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
- **sync** - Runs all the appropriate `./just` commands when checking out a new
version of voxel_globe. The intent is to run everything you *might* need to when
checking out a new version of voxel_globe to prevent side effects from having
pieces of voxel_globe from different git versions. You still need to run
`git submodule update` manually (or `git add` if that is the appropriate action)
Sync includes a `./just pull` step that will pull the latest docker images. If
you working with different docker images, you should call `build` first
(i.e. `./just build sync`). Alternatively you can set the `NOPULL` environment
variable too, but `./just build sync` is less prone to unexpected side effects.

### Debugging ###
- **debug** - Start a generic debian docker with access to all docker volumes
and directories. Your user credentials are copied and you start a bash session
as a user `user` with your uid and gid. Exiting that bash session with non-zero
will drop you down to a root terminal, still inside the same docker. This way 
you can debug as `user` or `root`.
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

### Configuring voxel-globe

There are many variables that can be added to `local_vip.env`. To enable DEBUG
capabilities (useful for development) add to `local_vip.env`

```
VIP_DEBUG=1
```

###Pull Requests

If you'd like to contribute to this project, please make a pull request. We'll review the pull request and discuss the changes. All pull request contributions to this project will be released under the MIT license.

Software source code previously released under an open source license and then modified by NGA staff is considered a "joint work" (see 17 USC § 101); it is partially copyrighted, partially public domain, and as a whole is protected by the copyrights of the non-government authors and must be released according to the terms of the original open source license.