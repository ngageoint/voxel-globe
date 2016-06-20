# Voxel Globe Docker #

## TL; DR ##

1. `git clone --recursive {voxel_globe repo}`
2. `cd {repo_directory}/docker`
3. `./just network` #Set up the voxel_globe docker network, only needs to be done once
4. `./just volume` #Create volumes needed
5. `./just build` #Build docker images, may take a while
6. `./just vxl` #compile library
7. `./just setup` #Initialize database
8. `./just start` #Start daemons
9. Open to web browser to http://localhost:8443/

## Fully automated install ##

`export VIP_CONFIRM_INITIALIZE_DATABASE=0` in your local_vip.env file, and the

## MacOSX and Windows ##

There are currently permissions issues when mounting the voxel_globe source
directory directly into a docker, making it hard to modify source files on the
host and have them be the same files in the docker. Currently Mac and Windows
need to copy the source directory into a docker volume and work off of those.
Further more, the postgresql database, image and storage directories need to be
docker volumes too.

# Rest of this document is out of date #

## Dockers ##

There are currently two type of dockers being created

1. Deploy dockers - Everything you need to run voxel_globe in a docker 
(Dockerfile). Currently it's one giant 23+GB Docker. The intent is to split
this up in the future and make AMD APP OpenCL SDK work an opencl a fallback. It
is not intended to use this, and all automatic script have commented it out.

2. Development docker - Everything you need to compile voxel_globe is in the 
docker, including the AMD APP OpenCL SDK, and CUDA SDK.

## Deploying ##

*TODO*

## Development ##

1. Build the docker 

    ./just build

The version of CUDA running in the host will automatically be identified (on CentOS) and 
installed in the docker (CUDA 5.5 to 7.5 currently supported). To override (or
if CUDA is not installed in the host) set the environment variable `CUDA_VERSION`

    CUDA_VERSION=7.0 ./just build

The NVIDIA drivers **MUST** be installed on the host and a compatible version 
of CUDA must be selected, but CUDA does not need to be installed in the host.

2. Create an NVIDIA driver volume. The [NVIDIA docker](https://github.com/NVIDIA/nvidia-docker)
project does this for you, but in the cast of CentOS, you can make one without
the NVIDIA plugin

    ./just volume

And all the NVIDIA driver files will be COPIED to the volume. This is different
than what NVIDIA does, but always works.

3. Build/compile/setup the current voxel_globe directory

    ./just setup

This will compile all packages in the docker, so that they will be ready to run
in the docker. This does not make them runnable outside the docker (unless you
have a LOT of dependencies installed in the host, which isn't the intent)

4) Run the docker image

    ./just run

This will start a bash session in the docker, set up the port forwards, mount
NVIDIA devices and the current code directory. This way you can edit files
outside the docker, and they are already the same files inside the docker

5) Inside the running docker container, start the daemons

    /opt/vip/daemon.bat all start

## OpenCL/OpenGL ##

- OpenCL currently works
- OpenGL currently does not work. I'm only missing some yum packages, I just
don't know which ones.

## Mac/Windows ##

Do not attempt CUDA/NVIDIA OpenCL, it won't work. Only use the AMD APP OpenCL SDK