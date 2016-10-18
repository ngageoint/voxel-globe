#!/usr/bin/env bash
#J.U.S.T. - J.U.S.T. uncomplicated simple tasking

set -euE
function print_error(){ echo "$1: line $2: Returned $?";}
trap 'print_error "${BASH_SOURCE[0]}" "${LINENO}"' ERR

#This windows check MUST be done first, or else the environment will be dirty
#This was the best idea, or else I'll have to use env -i and pick the 60+ 
#environment variables to be passed, that may vary, etc... bad idea

function is_powershell()
{
  if [ "${VIP_IS_POWERSHELL-0}" == "1" ]; then
    return 0
  fi

  local unique_title=$(head -c 16 /dev/urandom | xxd -pu)
  echo -en "\033]0;${unique_title}\a"
  if [ $(tasklist //fi "windowtitle eq ${unique_title}" | tail -n 1 | awk '{print $1}') == "powershell.exe" ]; then
    return 0
  else
    return 1
  fi
}

if [ "${OS-notwindows}" == "Windows_NT" ] && ! is_powershell; then
  env VIP_IS_POWERSHELL=1 start powershell "cmd /c color 07; bash $0 ${@+"${@}"}; bash --rcfile $(cd $(dirname ${BASH_SOURCE[0]}); pwd)/.winbashrc"
  exit 0
fi

if (( $# == 0 )); then
  exec $0 help
fi

CURDIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CURDIR}/vip.bsh
if [ -f "${VIP_VSI_DIR}/env.bsh" ]; then
  #In case the submodules haven't been checked out yet, during install
  source ${VIP_VSI_DIR}/env.bsh
  source ${VSI_COMMON_DIR}/linux/just_functions.bsh
  source ${VSI_COMMON_DIR}/linux/colors.bsh
  : ${VIP_JUST_COLOR_ERR=${ITALIC}}

  #Optionally in local_vip.env
  #COLORS_DEFAULT='(${RED} ${GREEN} $(FG 22))'
  if [ "${COLORS_DEFAULT+0}" == "0" ]; then
    eval "declare -a COLORS_DEFAULT=${COLORS_DEFAULT}"
  elif (( $(number_colors) < 88 )); then
    COLORS_DEFAULT=($RED $GREEN $YELLOW $MAGENTA $CYAN $WHITE)
  else
    COLORS_DEFAULT=($(FG {9..15} 19 28 38 48 68 94 126 244))
  fi
  COLORS=("${COLORS_DEFAULT[@]}")

  #Optionally in local_vip.env
  #COLOR_DB_DEFAULT='([redis_default]=${RED} [postgresql_default]=${GREEN} [celery_gpu]=$(FG 22))'
  if [ "${COLOR_DB_DEFAULT+0}" == "0" ]; then
    eval "declare -A COLOR_DB=${COLOR_DB_DEFAULT}"
  fi
fi

: ${DRYRUN=}

if [ "${DRYRUN}" == "" -a "${VIP_JUST_VERBOSE-0}" == "0" ]; then
  exec 3>/dev/null
  exec 4>/dev/null
else
  exec 3>&1
  exec 4>&2
fi

: ${DOCKER_RUN_ARGS=\
-e USER_ID=${VIP_DOCKER_USER_ID} \
-e GROUP_ID=${VIP_DOCKER_GROUP_ID} \
--label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
--label vip.service=undefined \
--label vip.node=default}
#Don't add --net to DOCKER_RUN_ARGS. It would be risky as many temporary 
#dockers that don't need an IP will be getting one, and this would
#significantly increase the changes an IP will change, thus breaking
#voxel_globe during partial restarts

: ${DOCKER=docker}
: ${NVIDIA_DOCKER=nvidia-docker}
if ! hash ${NVIDIA_DOCKER} 2> /dev/null; then
  NVIDIA_DOCKER=${DOCKER}
fi

function Exec-Nvidia-Docker(){ DOCKER_EXEC=1 USE_NVIDIA_DOCKER=1 Docker "${@}";}
function Nvidia-Docker(){ USE_NVIDIA_DOCKER=1 Docker "${@}";}
function Exec-Docker(){ DOCKER_EXEC=1 Docker "${@}";}
function Docker() #Helper function to execute the right docker command, or just echo
{
  local cmd

  if [ "${USE_NVIDIA_DOCKER-}" == "1" ]; then
    cmd=(${DRYRUN} ${NVIDIA_DOCKER})
  else
    cmd=(${DRYRUN} ${DOCKER})
  fi

  if [ "$1" == "run" ]; then
    cmd+=($1 ${DOCKER_RUN_ARGS})
    shift 1
  fi

  if [ "${DOCKER_EXEC-}" == "" ]; then
    command "${cmd[@]}" "${@}"
  else
    exec "${cmd[@]}" "${@}"
  fi
}

: ${JUST_NOPULL=0}

#List of images to push/pull
DOCKERHUB_IMAGE_NAMES=(${VIP_DOCKER_VXL_IMAGE_NAME}
                       ${VIP_DOCKER_POSTGRES_IMAGE_NAME}
                       ${VIP_DOCKER_RABBITMQ_IMAGE_NAME}
                       ${VIP_DOCKER_CELERY_IMAGE_NAME}
                       ${VIP_DOCKER_FLOWER_IMAGE_NAME}
                       ${VIP_DOCKER_NOTEBOOK_IMAGE_NAME}
                       ${VIP_DOCKER_REDIS_IMAGE_NAME}
                       ${VIP_DOCKER_DAPHNE_IMAGE_NAME}
                       ${VIP_DOCKER_ASGI_IMAGE_NAME}
                       ${VIP_DOCKER_UWSGI_IMAGE_NAME}
                       ${VIP_DOCKER_NGINX_IMAGE_NAME})

SERVICE_NAMES=(postgresql rabbitmq celery flower redis daphne asgi uwsgi nginx)

if [ "${VIP_DOCKER_USE_NOTEBOOK}" == 1 ]; then
  SERVICE_NAMES+=(notebook)
fi

function docker_create_volume()
{
  if docker volume inspect "$1" > /dev/null 2>&1; then
    if [ "${VIP_DOCKER_DELETE_VOLUME_ON_RESET}" == "1" ]; then
      echo "Deleting old $1 volume"
      Docker volume rm $1 >&3
    else
      return 0
    fi
  fi
  echo "Creating new $1 volume"
  docker volume create --name $1 >&3
  echo "Setting permissions on $1"

  docker run --rm -v "$(va ${1} /mnt)" debian:jessie chmod 777 ${WIN}/mnt
}

function find_containers()
{ # $1 - (optional) vip service name
  if (( $# > 0 )); then
    docker ps --filter=label=vip.service=${1} --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} ${find_args:+${find_args}} --format="{{.Names}}"
  else
    docker ps --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} ${find_args:+${find_args}} --format="{{.Names}}"
  fi
}

function find_node_containers()
{ # $1 - vip service name,  $2 - node name
  find_args=--filter=label=vip.node=${2} find_containers ${1}
}

function get_node_names()
{
  #Bash fun for array indirection with default value
  node_names=${1}
  if (( ${BASH_VERSINFO[0]} < 4 )); then
    node_names=$(echo VIP_${node_names}_NODES | tr '[a-z]' '[A-Z]')
  else
    node_names=VIP_${node_names^^}_NODES
  fi
  if [ "${!node_names-}" == "" ]; then
    node_names=(default)
  else
    node_names=${node_names}[@]
    node_names=("${!node_names}")
  fi
}

function pick_containers()
{
  local running_containers=()

  if (( ${#@} > 0 )); then
    for service_name in "${@}"; do
      running_containers+=($(find_containers ${service_name}))
    done
  else
    running_containers+=($(find_containers))
  fi

  if (( ${#running_containers[@]} == 0 )); then
    echo "No containers running" >&2
    exit 1
  elif (( ${#running_containers[@]} > 1)); then
    for c in $(seq 1 ${#running_containers[@]}); do
      if [ "${pick_gdb-0}" == "1" ]; then
        echo $c\):${running_containers[$(($c-1))]}:$(docker inspect -f '({{ (index (index .NetworkSettings.Ports "'${VIP_GDBSERVER_PORT}'/tcp") 0).HostPort }})' ${running_containers[$(($c-1))]})
      else
        echo $c\):${running_containers[$(($c-1))]}:"$(docker inspect -f '( {{(index .Config.Labels "vip.prefix")}}/{{(index .Config.Labels "vip.service")}}:{{(index .Config.Labels "vip.node")}}:)' ${running_containers[$(($c-1))]})"
      fi
    done | column -t -s : >&2
    read -r -p "Choose which container to enter: " cid
    if (( $cid >= 1 )) && (( $cid <= ${#running_containers[@]} )); then
      echo ${running_containers[$((${cid}-1))]}
    else
      echo "Invalid selection" >&2
      exit 1
    fi
  else
    echo ${running_containers[0]}
  fi
}

function enter_containers()
{
  local container=$(pick_containers ${@+"${@}"})
  Docker exec -it ${container} bash -c "echo 'import readline, rlcompleter;\
      readline.parse_and_bind(\"tab: complete\")' > /tmp/.pyrc;\
      exec env PYTHONSTARTUP=/tmp/.pyrc bash"
}

function pick_gdbcontainer()
{
  pick_gdb=1 pick_containers celery notebook
}

function django_command()
{
  #Usage: django_command [docker args --] command args
  local -a django_args=()
  local -a django_cmd=()

  while [ "${#@}" -gt "0" ]; do
    if [ "$1" == "${SEPARATOR---}" ]; then
      django_args=("${django_cmd[@]}")
      shift 1
      django_cmd=("${@}")
      break
    fi
    django_cmd+=($1)
    shift 1
  done

  Docker run --rm \
             -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
             -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
             -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
             -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
             -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
             -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
             -e VIP_OPENCL_DEVICE=cpu0 \
             --label vip.service=django_command \
             --net ${VIP_DOCKER_NETWORK} \
             -w ${WIN}/opt/vip/voxel_globe \
             ${django_args+"${django_args[@]}"} \
             ${VIP_DOCKER_CELERY_IMAGE_NAME} "${django_cmd[@]}"
}

GUI_ARGS=()

WIN= #Ming/cygwin hack

if [ "${VIP_OS}" == "Linux" ]; then
  GUI_ARGS+=(-v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY)
elif [ "${VIP_OS}" == "Windows" ]; then #Assume windows
  #export MSYS_NO_PATHCONV=1 #SHOULD work on the new git for windows
  #I just don't trust this MSYS_NO_PATHCONV option... wrote va function instead.
  WIN='/' #Ming/cygwin hack

  if [ "${DISPLAY}" == "needs-to-be-defined" ]; then 
    unset DISPLAY
    #stupid https://github.com/git-for-windows/build-extra/blob/d38b527afc552943769fcd8f252be0052ec9c874/git-extra/env.sh
  fi

  : ${DISPLAY=192.168.65.1:0}
  export DISPLAY
  GUI_ARGS+=(-e DISPLAY)
  #You have to be running xming or equivalent for this to work, of course
  #For windows, you have to set DISPLAY to IPAddress:0, it's impossible to 
  #determine this (correctly) programtically, thanks windows
  #I have no idea HOW 192.168.65.1 works, but I found it on the HyperV host 
  #and it "works"
elif [ "${VIP_OS}" == "Darwin" ]; then
  if [ "${DISPLAY+0}" == "0" ]; then
    GUI_ARGS+=(-e DISPLAY -v $(dirname $DISPLAY):$(dirname ${DISPLAY}))
  fi
  #I have not tested this yet, you probably need to start xquartz for it to work
else
  echo "What OS are you running?"
  exit 1
fi

function va()
{ #Convenient wrapper to deal with all the MINGW screw ups
  #Create all the volume argument for the -v argument for docker. What a pain
  #first argument is the host dir
  #second argument is the docker dir

  if [[ $# != 2 ]]; then
    echo "Something went wrong in mounting docker directory."
    echo "I hope I never see this error message..."
    exit 1
  fi

  #Create the directory before docker, or else it will be owned by ROOT! :(
  #Assume it's a directory because well... docker would too
  if is_dir_and_not_exist "$1"; then #if not a file or dir
    mkdir -p "$1" #make the dir
  fi

  if [ "${VIP_OS}" == "Windows" ]; then
    if (( ${BASH_VERSINFO[0]} > 3 )); then
      echo $(cygpath -w $1):${WIN}$2
      #Yes, bash 4 in mingw64 includes cygpath for some reason
      #Cygpath converts / -> \
      #^/{single letter} -> {single letter}:\
      #^/{single letter}/ -> {single letter}:\\ #bug?
      #else ^/ -> {git_directory}
    else
      echo $1:${WIN}$2
    fi
  else
    echo $1:$2
  fi
}

function in_array()
{
  local val=$1
  local x
  shift 1
  for x in "${@}"; do
    if [ "${x}" == "${val}" ]; then
      return 0
    fi
  done

  return 1
}

function is_service()
{
  if (( $# > 0 )); then
    in_array $1 "${SERVICE_NAMES[@]}"
    return $?
  fi
  return 1
}

function is_dir_and_not_exist()
{ #Simplifies checking if a string is a relative or absolute directory name,
  #and does not exist. This is needed because of a directory is replaced with
  #a volume name, it should not be created.

  local dir_name="$1"

  if ( [ "${dir_name:0:1}" == "/" ] || \
       ( (( ${#dir_name} >= 2 )) && [ "${dir_name:0:2}" == "./" ] ) ) && \
     [ ! -d "${dir_name}" ] && [ ! -e "${dir_name}" ]; then
     return 0 #TRUE!
  fi
   return 1 #False :(
}

declare -i extra_args

function caseify()
{
  local just_arg=$1
  extra_args=0
  shift 1

  case ${just_arg} in
    build) # Build all the docker images. Only needs to be done if you did not pull or modified the dockerfiles
      export JUST_NOPULL=1 #disable auto pulling from ./just sync
      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do
          echo "Building $1"
          (justify build_$1 1>&3 2>&4)
          shift 1
          extra_args+=1
        done
      else
        echo "Building vxl image"
        (justify build_vxl 1>&3 2>&4)
        (justify build "${SERVICE_NAMES[@]}")
      fi
      ;;
    build_postgresql)
      Docker build -t ${VIP_DOCKER_POSTGRES_IMAGE_NAME} \
                   -f ${CURDIR}/docker/postgresql.Dockerfile ${CURDIR}/docker
      ;;
    build_rabbitmq)
      Docker build -t ${VIP_DOCKER_RABBITMQ_IMAGE_NAME} \
                   -f ${CURDIR}/docker/rabbitmq.Dockerfile ${CURDIR}/docker
      ;;
    build_celery)
      Docker build -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                   -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      Docker build -t ${VIP_DOCKER_CELERY_IMAGE_NAME} \
                   -f ${CURDIR}/docker/celery.Dockerfile ${CURDIR}/docker
      Docker build -t ${VIP_DOCKER_CELERY_IMAGE_NAME}_gpu \
                   -f ${CURDIR}/docker/celery_gpu.Dockerfile ${CURDIR}/docker

      ;;
    build_vxl)
      Docker build -t ${VIP_DOCKER_VXL_IMAGE_NAME} \
                   -f ${CURDIR}/docker/vxl.Dockerfile ${CURDIR}/docker
      ;;
    build_flower)
      Docker build -t ${VIP_DOCKER_FLOWER_IMAGE_NAME} \
                   -f ${CURDIR}/docker/flower.Dockerfile ${CURDIR}/docker
      ;;
    build_notebook)
      Docker build -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                   -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      Docker build -t ${VIP_DOCKER_NOTEBOOK_IMAGE_NAME} \
                   -f ${CURDIR}/docker/notebook.Dockerfile ${CURDIR}/docker
      ;;
    build_nginx)
      Docker build -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                   -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      Docker build -t ${VIP_DOCKER_NGINX_IMAGE_NAME} \
                   -f ${CURDIR}/docker/nginx.Dockerfile ${CURDIR}/docker
      ;;
    build_uwsgi)
      Docker build -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                   -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      Docker build -t ${VIP_DOCKER_UWSGI_IMAGE_NAME} \
                   -f ${CURDIR}/docker/uwsgi.Dockerfile ${CURDIR}/docker
      ;;
    build_redis)
      Docker build -t ${VIP_DOCKER_REDIS_IMAGE_NAME} \
                   -f ${CURDIR}/docker/redis.Dockerfile ${CURDIR}/docker
      ;;
    build_daphne)
      Docker build -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                   -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      Docker build -t ${VIP_DOCKER_DAPHNE_IMAGE_NAME} \
                   -f ${CURDIR}/docker/daphne.Dockerfile ${CURDIR}/docker
      ;;
    build_asgi)
      Docker build -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                   -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      Docker build -t ${VIP_DOCKER_ASGI_IMAGE_NAME} \
                   -f ${CURDIR}/docker/asgi.Dockerfile ${CURDIR}/docker
      ;;

    build_rdm) #UNDOCUMENTED FEATURE build rdm image
      Docker build -t ${VIP_DOCKER_REPO}:rdm \
                   -f ${CURDIR}/docker/rdm.Dockerfile ${CURDIR}/docker
      ;;
    build_potree) #UNDOCUMENTED FEATURE build potree compiling image and compile potree. Argument is potree src dir
      Docker build -t ${VIP_DOCKER_REPO}:potree_builder \
                      -f ${CURDIR}/docker/build_potree.Dockerfile ${CURDIR}/docker
      Docker run --rm -v "$(va "$1" /potree)" \
                 ${VIP_DOCKER_REPO}:potree_builder
      extra_args+=1
      ;;
    build_winpdb) #UNDOCUMENTED FEATURE build winpdb
      Docker build -t ${VIP_DOCKER_REPO}:winpdb \
                   -f ${CURDIR}/docker/winpdb.Dockerfile ${CURDIR}/docker
      ;;
    build_code) #UNDOCUMENTED FEATURE build code image
      Docker build -t andyneff/code \
                   -f ${CURDIR}/docker/code.Dockerfile ${CURDIR}/docker
      ;;

    start) # Start all Voxel Globe containers. Optionally specify service names to only start specific containers
      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do

          get_node_names ${1}

          local -i running_nodes=0
          local status
          #Loop through all nodes, and delete "created" stuck containers
          for node_name in "${node_names[@]}"; do
            for container_name in $(find_node_containers ${1} ${node_name}); do
              status=$(docker inspect --type=container -f "{{.State.Status}}" ${container_name} 2>/dev/null)

              if [ "${status}" == "running" ]; then
                echo "$1(${node_name}) is already running"
                running_nodes+=1
              else
                if [ "${status}" == "created" ]; then
                  Docker rm ${container_name}
                fi
              fi
            done
          done

          #If all the nodes are not running, start them
          if (( ${running_nodes} < ${#node_names[@]} )); then
            echo "Starting $1"
            (justify clean_$1 start_$1 >& 3)
            #Its up to the individual clean_ and start_ to handle multiple nodes
          fi
          shift 1
          extra_args+=1
        done
      else #else start them ALL!
        (justify start ${SERVICE_NAMES[@]})
      fi
      ;;
    start_postgresql)
      local -a ADD_ARGS=()
      if [ "${VIP_POSTGRESQL_PUBLISH}" == "1" ]; then
        ADD_ARGS+=(-p ${VIP_POSTGRESQL_PORT}:${VIP_POSTGRESQL_PORT})

      fi

      Docker run -d ${ADD_ARGS+"${ADD_ARGS[@]}"} \
                 -v "$(va ${VIP_POSTGRESQL_DIR} ${VIP_POSTGRESQL_DIR_DOCK})" \
                 --name ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 --label vip.service=${just_arg#*_} \
                 -p ${VIP_POSTGRESQL_PORT}:${VIP_POSTGRESQL_PORT_DOCK} \
                 ${VIP_DOCKER_POSTGRES_IMAGE_NAME}
                 #-e POSTGRES_PASSWORD=${VIP_POSTGRESQL_PASSWORD}
      ;;
    start_rabbitmq)
      Docker run -d -v "$(va ${VIP_RABBITMQ_VOLUME} ${VIP_RABBITMQ_DIR_DOCK})" \
                 -p 15672:15672 \
                 --label vip.service=${just_arg#*_} \
                 --name ${VIP_DOCKER_RABBITMQ_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 ${VIP_DOCKER_RABBITMQ_IMAGE_NAME}
      ;;
    start_nginx)
      Docker run -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_CONF_DIR} /usr/local/apache2/conf)" \
                 -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -v "$(va ${VIP_NGINX_SSL_VOLUME} ${VIP_NGINX_SSL_DIR_DOCK})" \
                 --name ${VIP_DOCKER_NGINX_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 -p ${VIP_NGINX_PORT}:${VIP_NGINX_PORT_DOCK} \
                 -p ${VIP_NGINX_SSL_PORT}:${VIP_NGINX_SSL_PORT_DOCK} \
                 --label vip.service=${just_arg#*_} \
                 -e VIP_OPENCL_DEVICE=cpu0 \
                 -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                 -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                 ${VIP_DOCKER_NGINX_IMAGE_NAME}
      ;;
    start_celery)
      local -a OTHER_ARGS=()
      if [ "${VIP_GDBSERVER}" == "1" ]; then
        #--security-opt=seccomp:unconfined : needed for --attach pid#
        #--security-opt apparmor:unconfined : needed for --multi (not currently using)
        #--cap-add SYS_PTRACE : needed for ptrace
        #https://github.com/docker/docker/issues/7276
        OTHER_ARGS+=(--cap-add SYS_PTRACE 
                     --security-opt=seccomp:unconfined 
                     --security-opt apparmor:unconfined 
                     -p ${VIP_GDBSERVER_PORT}
                     -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})")
      fi

      for i in ${!VIP_CELERY_NODES[@]}; do
        if [ "$(find_node_containers ${just_arg#*_} ${VIP_CELERY_NODES[$i]})" == "" ]; then
          local image=${VIP_DOCKER_CELERY_IMAGE_NAME}

          if docker inspect --type=image ${image}_${VIP_CELERY_NODES[$i]%%_*} >& /dev/null; then
            image+=_${VIP_CELERY_NODES[$i]%%_*}
          fi

          local extra_args=VIP_CELERY_ARGS_${VIP_CELERY_NODES[i]}[@]

          Nvidia-Docker run -d \
                     -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                     -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                     -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                     -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                     --label vip.service=${just_arg#*_} \
                     --label vip.node=${VIP_CELERY_NODES[$i]} \
                     -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                     -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                     -e NODE_NAME=${VIP_CELERY_NODES[$i]} \
                     -e VIP_CELERY_QUEUES -e VIP_CELERY_EXCHANGES -e VIP_CELERY_KEYS \
                     --name ${VIP_DOCKER_CELERY_CONTAINER_NAME}-$i \
                     --net ${VIP_DOCKER_NETWORK} \
                     --hostname ${VIP_DOCKER_CELERY_CONTAINER_NAME}-$i \
                     ${OTHER_ARGS[@]+"${OTHER_ARGS[@]}"} \
                     ${image} celery \
                     ${VIP_CELERY_DEFAULT_ARGS+"${VIP_CELERY_DEFAULT_ARGS[@]}"} \
                     ${!extra_args+"${!extra_args}"}
        else
          echo "celery node ${VIP_CELERY_NODES[$i]} is already running"
        fi
      done
      ;;
    start_redis)
      Docker run -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_REDIS_VOLUME} ${VIP_REDIS_DIR_DOCK})" \
                 --label vip.service=${just_arg#*_} \
                 --name ${VIP_DOCKER_REDIS_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 ${VIP_DOCKER_REDIS_IMAGE_NAME}
      ;;
    start_daphne)
      Docker run -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 --label vip.service=${just_arg#*_} \
                 --name ${VIP_DOCKER_DAPHNE_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 ${VIP_DOCKER_DAPHNE_IMAGE_NAME}
      ;;
    start_asgi)
      Docker run -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                 -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                 -e VIP_OPENCL_DEVICE=cpu0 \
                 --label vip.service=${just_arg#*_} \
                 --name ${VIP_DOCKER_ASGI_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 ${VIP_DOCKER_ASGI_IMAGE_NAME}
      ;;
    start_uwsgi)
      Docker run -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                 -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                 -e VIP_OPENCL_DEVICE=cpu0 \
                 -e VIP_UWSGI_DEPLOY_ON_START \
                 --label vip.service=${just_arg#*_} \
                 --name ${VIP_DOCKER_UWSGI_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 ${VIP_DOCKER_UWSGI_IMAGE_NAME}
      ;;

    gdbserver) # Start gdbserver in the notebook/celery worker in multi mode
      local container=$(pick_gdbcontainer)
      local port=$(docker inspect -f '{{ (index (index .NetworkSettings.Ports "'${VIP_GDBSERVER_PORT}'/tcp") 0).HostPort }}' ${container})
      echo Connect your favorite gdb debugger to localhost:${port}
      cat > ${CURDIR}/gdbinit << EOF
target extended-remote localhost:${port} > ${CURDIR}/gdbinit
directory ${VIP_PROJECT_DIR}/external
EOF
      #set auto-load safe-path / Doesn't help
      
      Docker exec -it ${container} gdbserver --multi 0.0.0.0:${VIP_GDBSERVER_PORT}
      ;;

    gdbserver2) # Start gdbserver in the notebook/celery worker attaching to a specific pid
      local container=$(pick_gdbcontainer)

      Docker exec -it ${container} ps -ef
      read -r -p "Choose which pid to attach to: " pid

      local port=$(docker inspect -f '{{ (index (index .NetworkSettings.Ports "'${VIP_GDBSERVER_PORT}'/tcp") 0).HostPort }}' ${container})
      echo Connect your favorite gdb debugger to localhost:${port}
      echo "directory ${VIP_PROJECT_DIR}/external" >> ${CURDIR}/gdbinit
      Docker exec -it ${container} gdbserver --attach 0.0.0.0:${VIP_GDBSERVER_PORT} ${pid}
      ;;

    gdb) #Run gdb in TUI mode, by attaching to a specific PID. Optional argument is the PID #, else it will list all the available PIDs and prompt
      local container=$(pick_gdbcontainer)
      local pid

      if [ "${#@}" == 0 ]; then
        Docker exec -it ${container} ps -ef
        read -r -p "Choose which pid to attach to: " pid
      else
        pid=$1
      fi

      Exec-Docker exec -it ${container} env TERM=${TERM} COLUMNS=$(tput cols) LINES=$(tput lines) gdb -tui -p ${pid}
      ;;

    ssh-keygen)
      local container=$(pick_gdbcontainer)
      docker exec ${container} bash -c 'if ! pgrep sshd; then
                                          ssh-keygen -P "" -f ~/.ssh/id_rsa && 
                                          cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys &&
                                          /usr/sbin/sshd
                                        fi'
      docker cp ${container}:/root/.ssh/id_rsa ${CURDIR}/gdb_rsa

      ;;

    start_flower)
      Docker run -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 --name ${VIP_DOCKER_FLOWER_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 --label vip.service=${just_arg#*_} \
                 -p ${VIP_FLOWER_PORT}:${VIP_FLOWER_PORT_DOCK} \
                 ${VIP_DOCKER_FLOWER_IMAGE_NAME}
      ;;
    start_notebook)
      local -a OTHER_ARGS=()
      if [ "${VIP_GDBSERVER}" == "1" ]; then
        OTHER_ARGS+=(--cap-add SYS_PTRACE --security-opt=seccomp:unconfined --security-opt apparmor:unconfined -p ${VIP_GDBSERVER_PORT})
      fi

      Docker run -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                 -v "$(va ${VIP_NOTEBOOK_DIR} ${VIP_NOTEBOOK_DIR_DOCK})" \
                 -v "$(va ${VIP_NOTEBOOK_CONFIG_DIR} ${VIP_NOTEBOOK_CONFIG_DIR_DOCK})" \
                 -v "$(va ${VIP_NOTEBOOK_CUSTOM_DIR} ${VIP_NOTEBOOK_CUSTOM_DIR_DOCK})" \
                 -v "$(va ${VIP_NOTEBOOK_MPL_VOLUME} ${VIP_NOTEBOOK_MPL_DIR_DOCK})" \
                 --name ${VIP_DOCKER_NOTEBOOK_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 -p ${VIP_NOTEBOOK_PORT}:${VIP_NOTEBOOK_PORT_DOCK} \
                 --label vip.service=${just_arg#*_} \
                 -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                 -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                 ${OTHER_ARGS[@]+"${OTHER_ARGS[@]}"} \
                 ${VIP_DOCKER_NOTEBOOK_IMAGE_NAME}
      ;;


    stop) # Stop all Voxel Globe containers. Optionally specify service names to only stop specific containers
      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do
          echo "Stopping $1"
          (justify stop_$1 >& 3)
          shift 1
          extra_args+=1
        done
      else
        #stop them ALL! (in reverse order)
        for (( idx=${#SERVICE_NAMES[@]}-1 ; idx>=0 ; idx-- )) ; do
          (justify stop "${SERVICE_NAMES[idx]}" || :)
        done
      fi
      ;;
    stop_postgresql)
      # || : because 1) you WANT them all to run, and 2) pg_ctl doens't return 0
      for container_name in $(find_containers ${just_arg#*_}); do
        Docker exec ${container_name} gosu postgres pg_ctl stop || :
        echo #pg_ctl stop output is missing newline
      done
      ;;
    stop_rabbitmq)
      for container_name in $(find_containers ${just_arg#*_}); do
        Docker exec ${container_name} rabbitmqctl stop || :
      done
      ;;
    stop_celery)
      local node_name
      for container_name in $(find_containers ${just_arg#*_}); do
        node_name=$(docker inspect -f '{{ (index .Config.Labels "vip.node")}}' ${container_name})
        Docker exec ${container_name} bash -c "cd /home/user && gosu user celery multi stop ${node_name}" || :
      done
      ;;
    stop_*)
      #Many of the stop commands return non-zero
      Docker stop "$(find_containers ${just_arg#*_})" || :
      ;;

    force-stop) # Forcefully stop all Voxel Globe containers. Optionally specify service names to only stop specific containers
      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do
          echo "Forcefully stopping $1"
          (justify force-stop_$1 >& 3)
          shift 1
          extra_args+=1
        done
      else
        #stop them ALL! (in reverse order)
        for (( idx=${#SERVICE_NAMES[@]}-1 ; idx>=0 ; idx-- )) ; do
          (justify force-stop "${SERVICE_NAMES[idx]}" || :)
        done
      fi
      ;;
    force-stop_*)
      (justify kill ${just_arg#*_})
      ;;


    wait) # Wait for all Voxel Globe containers to stop. Optionally specify service names to only wait on specific containers
      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do
          (justify wait_$1 >& 3)
          shift 1
          extra_args+=1
        done
      else
        (justify wait "${SERVICE_NAMES[@]}")
      fi
      ;;
    wait_*)
      for container_name in $(find_containers ${just_arg#*_}); do
        Docker wait ${container_name} || :
      done
      ;;


    restart) # Restart all Voxel Globe containers. Optionally specify service names to only restart specific containers
      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do
          (justify restart_$1)
          shift 1
          extra_args+=1
        done
      else
        echo [Stopping containers]
        (justify stop)
        echo [Waiting for containers to stop]
        (justify wait)
        echo [Starting containers]
        (justify start)
      fi
      ;;
    restart_*)
      (justify stop ${just_arg#*_} wait ${just_arg#*_} start ${just_arg#*_})
      ;;
    quick-restart) # Same as 'restart', except a few services restart faster in same container. Not useful for reloading environment
      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do
          (justify quick-restart_$1)
          shift 1
          extra_args+=1
        done
      else
        (justify quick-restart ${SERVICE_NAMES[@]})
      fi
      ;;
    quick-restart_nginx)
      for container_name in $(find_containers ${just_arg#*_}); do
        Docker exec -i ${container_name} ${WIN}${VIP_PROJECT_DIR_DOCK}/wrap \
          bash -c 'ep -d /dev/stdin > /etc/nginx/nginx.conf 2>/dev/null && \
                   nginx -s reload' < ${VIP_NGINX_CONF}
      done
      ;;
    quick-restart_uwsgi)
      for container_name in $(find_containers ${just_arg#*_}); do
        Docker kill --signal=SIGHUP ${container_name}
      done
      ;;
    quick-restart_*)
      (justify stop ${just_arg#*_})
      (justify wait ${just_arg#*_})
      (justify start ${just_arg#*_})
      ;;


    kill) # Kill all Voxel Globe containers. Use this when 'stop' does not work (times out)
      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do
          (justify kill_$1)
          shift 1
          extra_args+=1
        done
      else
        (justify kill "${SERVICE_NAMES[@]}")
      fi
      ;;
    kill_all)
      for container_name in $(find_containers); do
        Docker kill --signal ${KILL_SIGNAL-9} ${container_name}  
      done
      ;;
    kill_*)
      for container_name in $(find_containers ${just_arg#*_}); do
        Docker kill --signal ${KILL_SIGNAL-9} ${container_name}  
      done
      ;;


    push) # Push docker images to docker hub
      for image_name in "${DOCKERHUB_IMAGE_NAMES[@]}"; do
        Docker push ${image_name}
      done
      ;;
    pull) # Pull docker images from docker hub. Used this instead of 'build' if you are not modifying images yourself
      for image_name in "${DOCKERHUB_IMAGE_NAMES[@]}"; do
        Docker pull ${image_name}
      done
      ;;


    ssh-submodule) #Convert submodules to git protocol
      sed -Ei 's|https://([a-zA-Z0-9._-]*)/|git@\1:|' ${CURDIR}/.gitmodules
      echo "You can now run 'git submodule sync' then 'git checkout .gitmodules'"
      ;;
    https-submodule) #Convert submodules to https protocol
      sed -Ei 's|git@([a-zA-Z0-9._-]*):|https://\1/|' ${CURDIR}/.gitmodules
      echo "You can now run 'git submodule sync' then 'git checkout .gitmodules'"
      ;;

    public-release) #Function to prepare repo for public release
      #Todo
      ;;


    clean) # Remove all dead Voxel Globe containers. Optionally specify service names to only clean specific containers
      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do
          (justify clean_$1 >&3)
          shift 1
          extra_args+=1
        done
      else
        (justify clean "${SERVICE_NAMES[@]}")
      fi
      ;;
    clean_*)
      for container_id in $(find_args=-a find_containers ${just_arg#*_}); do
        if [ "$(docker inspect -f '{{.State.Status}}' --type container ${container_id} 2>/dev/null)" != "running" ]; then
          Docker rm ${container_id}
        fi
      done
      ;;


    log) # Show logs from all Voxel Globe containers. Optionally specify service names to only start specific containers
      function kill_logs()
      {
        for pid in "${LOG_PIDS[@]}"; do
          if [ "${VIP_OS}" == "Windows" ]; then
            local children=$(ps -f | grep $pid | awk '{print $2}' | grep -v $pid)
          else
            local children=$(pgrep -P $pid)
          fi

          kill -9 $pid
          wait $pid 2>/dev/null || : #Wait for while to to die
          kill -9 $children || : #Kill docker-log command, the rest will clean up
          #In windows, this children kill sometimes isn't needed?
        done
        # for pid_group in $(ps h -o "%r" "${LOG_PIDS[@]}" | uniq); do
        #   echo "Killing pid group $pid_group"
        #   kill -TERM -${pid_group}
        #   echo "Killed pid group $pid_group"
        # done
        echo #Ctrl+C doesn't have a newline
      }

      function print_waiting_logs()
      {
        log_wait_again=1
        local pid
        for pid in "${LOG_PIDS[@]}"; do
          kill -USR1 $pid
        done
      }

      function list_logs()
      {
        local c
        log_wait_again=1
        for c in "${!COLOR_DB[@]}"; do
          echo "${COLOR_DB[${c}]}${c}${NC}"
        done
      }

      function start_log_tail()
      { #service_name node_name color
        echo "$3 $1 ($2) ${NC}"

        local cmd="find_container(){
                     docker ps -a --filter=label=vip.service=$1 --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} --filter=label=vip.node=$2 --format={{.Names}};
                   };"

        if ! ( [ "${VIP_OS}" == "Windows" ] && (( ${BASH_VERSINFO[0]} < 4 )) ); then
          cmd+="print_wait_status(){ 
                  echo \"Currently waiting on ${3}${1}${NC}\";
                };
                trap print_wait_status USR1;"
        fi

        local sed_cmd
        if [ "${VIP_OS}" == "Darwin" ]; then
          sed_cmd='sed -l'
        else
          sed_cmd='sed -u'
        fi
        
        cmd+="while :; do \
                container=\$(find_container);
                if [ \"\${container}\" != \"\" ]; then
                  docker logs -f --tail=20 \$(find_container) "

        if [ "${VIP_OS}" == "Windows" ] && (( ${BASH_VERSINFO[0]} < 4 )); then
          cmd+="  | ${sed_cmd} 's|^|$3|' | ${sed_cmd} 's|$|${NC}|';"
        else
          cmd+="  2> >(${sed_cmd} 's|^|${VIP_JUST_COLOR_ERR}$3|' | ${sed_cmd} 's|$|${NC}|') \
                  1> >(${sed_cmd} 's|^|$3|' | ${sed_cmd} 's|$|${NC}|');"
        fi

        cmd+="  fi;"

        if [ "${VIP_OS}" == "Windows" ]; then
          cmd+="sleep 2;"
          #Added sleep for 2 seconds for windows. Ctrl+C actually kills the 
          #docker logs in windows, meaning the children kill is less then 
          #necessary. But at least this way I have TWO seconds to go from the
          #local children= line to the first kill. So should be good
        fi

        cmd+="  first_message=echo; "'
                while [ "$(docker inspect --type=container -f {{.State.Status}} $(find_container) 2>/dev/null)" != "running" ]; do '"
                  \$first_message Waiting for $1 \($2\) to start...;
                  first_message=: ;
                  sleep 0.5;
                done;
                echo Found $1 \($2\);
              done"

        bash -c "${cmd}"&
        LOG_PIDS+=($!)
      }

      trap print_waiting_logs USR1
      trap list_logs USR2
      trap kill_logs INT
      trap kill_logs TERM
      local -a LOG_PIDS=()

      local watch_services=()

      if is_service ${@+"${1}"}; then
        while is_service ${@+"${1}"}; do
          watch_services+="${1}"
          shift 1
          extra_args+=1
        done
      else
        watch_services=("${SERVICE_NAMES[@]}")
      fi

      for service_name in "${watch_services[@]}"; do
        get_node_names ${service_name}
        for node_name in "${node_names[@]}"; do
          get_color ${service_name}_${node_name}
          start_log_tail ${service_name} ${node_name} $(get_color ${service_name}_${node_name})
        done
      done

      local log_wait_again=1
      while [ "${log_wait_again}" == "1" ]; do
        log_wait_again=0
        wait "${LOG_PIDS[@]}" 2>/dev/null || :
      done

      trap - USR1
      trap - USR2
      trap - INT
      trap - TERM
      ;;
    log_wait)
      # Mostly useless feature that will cause each log tail to echo out if it
      # is currently waiting for a service to start again. This is useful to
      # make sure the logs are stuck again. They don't seem to get stuck anymore
      pkill -USR1 -f "just log"
      ;;
    log_list)
      # Mostly useless feature that will cause each just log to echo out the list
      # of watching loggers and associated colors
      pkill -USR2 -f "just log"
      ;;


    enter) # Enter a running container and start an interactive bash session. If you do not specify a specific service, a list will be supplied
      if is_service ${@+"${1}"}; then
        (justify enter_$1)
        shift 1
        extra_args+=1
      else
        enter_containers
      fi
      ;;
    enter_*)
      enter_containers ${just_arg#*_}
      ;;


    vxl) # Compile external/vxl_src in a docker for use by the other containers
      if [ "${VIP_OS}" == "Windows" ]; then
        local VXL_ARGS=(-e NUMBER_OF_PROCESSORS=2)
      fi
      Docker run -it --rm \
                 -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -e VIP_VXL_CMAKE_ENTRIES \
                 -e VIP_VXL_BUILD_TYPE \
                 ${VXL_ARGS[@]+"${VXL_ARGS[@]}"} \
                 ${VIP_DOCKER_VXL_IMAGE_NAME}
      ;;
    vxl-cmake) # Force Cmake to re-run on the vxl build
      Docker run -it --rm \
                 -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -w ${WIN}${VIP_VXL_DIR_DOCK}/build/${VIP_VXL_BUILD_TYPE} \
                 ${VIP_DOCKER_VXL_IMAGE_NAME} cmake . ${VIP_VXL_CMAKE_ENTRIES}
      ;;
    vxl-debug) # Enter the vxl build docker for easier debugging. Ideal for boxm2_ocl_render_view
      Exec-Nvidia-Docker run -it --rm "${GUI_ARGS[@]}" \
          -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
          -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
          -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
          -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
          -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
          ${VIP_DOCKER_VXL_IMAGE_NAME} bash -c \
          "groupadd user -g $(id -g); 
           useradd -u $(id -u) -o -m -d /home/user -s \`command -v bash\` -g user user; 
           ldconfig;
           echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd && \
           echo 'export PATH=/usr/local/nvidia/bin:${PATH}:/usr/local/sbin:/usr/sbin:/sbin:/vxl/bin' >> ~user/.bashrc;
           su user ${@} || bash"
      ;;
    network) #Initialize Voxel Globe Docker network, only needs to be done once
      if ! docker network inspect ${VIP_DOCKER_NETWORK} > /dev/null 2>&1; then
        Docker network create ${VIP_DOCKER_NETWORK}
      fi
      ;;
    initialize-database) # WARNING: this will WIPE an existing database. Initialize database. Must do this before using Django
      #Start database, AND initialize for the first time probably
      local stop_database=0

      if [ "$(docker inspect --type=container -f "{{.State.Status}}" $(find_containers postgresql | head -n1) 2>/dev/null)" != "running" ]; then
        stop_database=1
        (justify start postgresql)
      fi

      #Initialize database
      django_command -it -e VIP_VXL_SILENT_FAIL_IMPORT=1 \
                         -e VIP_INITIALIZE_DATABASE_CONFIRM -- \
                     ${WIN}${VIP_PROJECT_DIR_DOCK}/data/initialize_database.py

      if [ "${stop_database}" == "1" ]; then
        #Stop database
        (justify stop postgresql)
      fi
      ;;
    collect-static) # Prepare and collect static files for use in uwsgi (and potentially asgi) and test webserver. Must be done every time static libraries are changed
      django_command -e VIP_VXL_SILENT_FAIL_IMPORT=1 -- \
                     ${WIN}${VIP_PROJECT_DIR_DOCK}/voxel_globe/static_common/deploy.py

      ;;
    reset-volume) # WARNING: This will probably DESTROY and internal docker volumes. Creates initial storage volumes
      echo "Creating other volumes"

      for volume_name in ${VIP_RABBITMQ_VOLUME} ${VIP_VXL_VOLUME} ${VIP_NOTEBOOK_MPL_VOLUME} ${VIP_NGINX_SSL_VOLUME} ${VIP_REDIS_VOLUME}; do
        docker_create_volume ${volume_name}
      done

      if is_dir_and_not_exist "${VIP_IMAGE_DIR}"; then
        mkdir -p ${VIP_IMAGE_DIR}
        chmod 777 ${VIP_IMAGE_DIR}
      fi
      if is_dir_and_not_exist "${VIP_STORAGE_DIR}"; then
        mkdir -p ${VIP_STORAGE_DIR}
        chmod 777 ${VIP_STORAGE_DIR}
      fi
      ;;
    windows-volume) # WARNING: This will probably DESTROY IMAGES and STORAGE internal docker volumes!!! Create initial storage volumes for windows
      echo "Creating windows specific volumes"
      for volume_name in ${VIP_POSTGRESQL_DIR} ${VIP_STORAGE_DIR} ${VIP_IMAGE_DIR}; do
        docker_create_volume ${volume_name}
      done

      Docker run --rm \
                 -v "$(va ${VIP_STORAGE_DIR} /storage)" \
                 -v "$(va ${VIP_IMAGE_DIR} /image)" \
                 debian:jessie chmod 777 ${WIN}/image ${WIN}/storage
      ;;
    dev) # Conveniently run developer tasks, like migrating database, etc...
      DOCKER_EXEC="1" django_command -it -e VIP_OS -- ${WIN}/opt/vip/dev.bsh
      ;;
    sync) # Helper for the dev that runs through all possible sync operations. Useful to call after any git merge "J.U.S.T. in case"
      (justify stop)
      if [ "${JUST_NOPULL}" == "0" ]; then
        (justify pull)
      fi
      echo "Rebuiling vxl and http static files"
      (justify vxl-cmake vxl)
      (justify collect-static >& 3)
      (justify start postgresql)
      echo "Migrating database"
      (justify manage migrate >& 3)
      (justify stop postgresql)
      #git submodule update?
      echo 
      echo "You can run '$0 start' now..."
      ;;
    install) #Full install default path
      (justify reset-volume)
      if [ "${VIP_OS}" == "Windows" ]; then
        (justify windows-volume)
      fi
      if [ "${JUST_NOPULL}" == "0" ]; then
        (justify pull)
      fi
      #there is too much potential for error here, always 
      (justify vxl 1>&1 2>&3)
      echo "Configuring docker network"
      (justify network)
      echo "Initilizing database"
      (VIP_INITIALIZE_DATABASE_CONFIRM=0 justify initialize-database)
      echo "Setting up static files"
      (justify collect-static)
      ;;
    ps) # List all Voxel Globe containers and their statuses
      Docker ps -a --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX}
      ;;
    telnet) # Start a telnet docker. Useful for python debuggers that need a telnet connection. All additional arguments are sent to telnet command
      Exec-Docker run -it --rm --net ${VIP_DOCKER_NETWORK} \
                                 jess/telnet ${@+"${@}"}
      ;;
    debug) # Start and enter a special debug docker. Mainly useful in accessing docker volumes. Type 'exit 1' to become root
      local tag=$1
      shift 1
      Exec-Nvidia-Docker run -it --rm --net ${VIP_DOCKER_NETWORK} \
                             -v "$(va ${VIP_RABBITMQ_VOLUME} /rabbitmq)" \
                             -v "$(va ${VIP_POSTGRESQL_DIR} /postgres)" \
                             -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                             -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                             -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                             -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                             -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                             -v "$(va ${VIP_REDIS_VOLUME} /redis)" \
                             -v "$(va ${VIP_NOTEBOOK_MPL_VOLUME} ${VIP_NOTEBOOK_MPL_DIR_DOCK})" \
                             -v "$(va ${VIP_NGINX_SSL_VOLUME} ${VIP_NGINX_SSL_DIR_DOCK})" \
                             "${GUI_ARGS[@]}" \
                             --entrypoint bash \
                             ${VIP_DOCKER_REPO}:${tag} -c "groupadd user -g $(id -g) -o && \
                                 useradd -u $(id -u) -o --create-home --home-dir /home/user -g user user && \
                                 echo 'import readline, rlcompleter; \
                                 readline.parse_and_bind(\"tab: complete\")' > /tmp/.pyrc && \
                                 export PYTHONSTARTUP=/tmp/.pyrc && \
                                 gosu user bash ${@} || bash"
      ;;
    winpdb) # Start winpdb. Useful for graphically debugging python remotely. All additional arguments are sent to winpdb
      Exec-Docker run -it --rm --net ${VIP_DOCKER_NETWORK} \
                      "${GUI_ARGS[@]}" \
                      --label vip.service=${just_arg#*_} \
                      ${VIP_DOCKER_REPO}:winpdb winpdb ${@+"${@}"}
      ;;
    code) # Start MS VS Code. Useful for graphically debugging C++ remotely. All additional arguments are sent to code
      local -a args
      if [ "$#" == "0" ]; then
        args=(${WIN}/vxl_src)
      else
        args=("${@}")
      fi
      Exec-Docker run -it --rm --net ${VIP_DOCKER_NETWORK} \
                      "${GUI_ARGS[@]}" \
                      -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                      -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                      -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                      --label vip.service=${just_arg#*_} \
                      andyneff/code code "${args}"
      ;;

    rdm) #Run Redis Desktop Manager to debug redis database
      Exec-Nvidia-Docker run --rm \
                         "${GUI_ARGS[@]}" \
                         --label vip.service=${just_arg#*_} \
                         --net ${VIP_DOCKER_NETWORK} \
                         ${VIP_DOCKER_REPO}:rdm ${@+"${@}"}
      ;;
    copy-python) # Copy python libraries from service container into external dir
      local container_name=$1
      extra_args+=1
      mkdir -p ${VIP_PROJECT_DIR}/external/python_libs/${container_name}
      docker cp vip-${container_name}:/usr/local/lib/python2.7 ${VIP_PROJECT_DIR}/external/python_libs/${container_name}
      ;;
    runserver) # Runs runserver
      DOCKER_EXEC=1 django_command -it \
          -p ${VIP_START_MANAGE_PORT}:${VIP_START_MANAGE_DOCK_PORT} -- \
          ${WIN}/opt/vip/wrap python manage.py runserver 0.0.0.0:${VIP_START_MANAGE_DOCK_PORT}
      ;;
    manage) # Run django manage.py script. All additional arguments are sent to manage.py
      DOCKER_EXEC=1 django_command -it -- \
          ${WIN}/opt/vip/wrap python manage.py ${@+"${@}"}
      ;;
    ip) # Helper to print out the name and ip address of a service. No argument will list all ips, else an argument of service name, or manage
      local containers
      if [ "$#" == "0" ]; then
        containers="$(find_containers)"
      else
        containers="$(find_containers $1)"
        extra_args+=1
      fi
      docker inspect --format="{{.Name}}"$'\t'"{{.NetworkSettings.Networks.${VIP_DOCKER_NETWORK}.IPAddress}}" \
                     ${containers}
      ;;

    django-password) # Sets the hashes in the the django password shadow file. Use reset-password to apply these changes
      django_command -it -- ${WIN}/opt/vip/wrap python ${WIN}/opt/vip/shadow/make_django_password.py
      ;;
    reset-password) # Resets user passwords based on stored shadow files
      django_command -it -e VIP_OS -- \
                     ${WIN}/opt/vip/wrap python \
                     ${WIN}/opt/vip/shadow/initialize_users.py
      ;;

    psql) # Run psql in postgresql container in non tty mode. Useful for piping files to psql
      local -a postgresql_containers=($(find_containers postgresql))
      Exec-Docker exec -i ${postgresql_containers[0]} \
                       gosu ${VIP_POSTGRESQL_USER} psql ${@+"${@}"}
      ;;
    psqli) # Run psql in postgresql container in tty mode. Useful for interactive session
      local -a postgresql_containers=($(find_containers postgresql))
      Exec-Docker exec -it ${postgresql_containers[0]} \
                       gosu ${VIP_POSTGRESQL_USER} psql ${@+"${@}"}
      ;;
    pg_dump) # Dump database to stdout. Usage ./just pg_dump > my_database.sql
      local -a postgresql_containers=($(find_containers postgresql))
      Exec-Docker exec ${postgresql_containers[0]} \
                       gosu ${VIP_POSTGRESQL_USER} pg_dump ${VIP_POSTGRESQL_DATABASE_NAME}
      ;;
    pg_restore) # Drops the database, and reads in from file specified as next argument. Usage ./just pg_restore my_database.sql
      local -a postgresql_containers=($(find_containers postgresql))
      echo "Restoring ${VIP_POSTGRESQL_DATABASE_NAME} using $1"
      Docker exec ${postgresql_containers[0]} \
                  gosu ${VIP_POSTGRESQL_USER} \
                  dropdb ${VIP_POSTGRESQL_DATABASE_NAME} || :
      Docker exec ${postgresql_containers[0]} \
                  gosu ${VIP_POSTGRESQL_USER} \
                  createdb ${VIP_POSTGRESQL_DATABASE_NAME}
      Docker exec -i ${postgresql_containers[0]} \
                  gosu ${VIP_POSTGRESQL_USER} \
                  psql -d ${VIP_POSTGRESQL_DATABASE_NAME} < "$1"
      extra_args+=1
      ;;
    django-dump) #Dumps the django database to stdout in json format. Usage just django-dump ./dir/my_database.json
      local filename=$(real_path $1) #get real absolute path
      touch ${filename} #make sure it exists, or else docker will make it a dir
      django_command \
          -v "$(va ${filename} /database_dump.json)" -- \
          ${WIN}/opt/vip/wrap python manage.py dumpdata -o ${WIN}/database_dump.json
      extra_args+=1
      ;;
    django-load) #Loads the django data from a json file
      local filename=$(real_path $1) #get real absolute path

      django_command \
          -it -v "$(va ${filename} /database_dump.json)" -- \
          ${WIN}/opt/vip/wrap python manage.py loaddata ${WIN}/database_dump.json
      extra_args+=1
      ;;

    le-cert) # Runs let's encrypt, registering domain name supplied as an argument
      local -a nginx_containers=($(find_containers nginx))
      Docker exec ${nginx_containers[0]} ${WIN}/opt/vip/wrap \
                  ${WIN}/opt/certbot/bin/certbot certonly -n --webroot \
                  --agree-tos --email admin@visionsystemsinc.com \
                  --webroot-path ${WIN}/tmp --domains=$1 
      extra_args+=1
      ;;
    le-renew) #Renews let's encrypt certificates
      local -a nginx_containers=($(find_containers nginx))
      Docker exec ${nginx_containers[0]} ${WIN}/opt/vip/wrap \
                  ${WIN}/opt/certbot/bin/certbot renew
      ;;

    update-python-requirements) #update requirements.txt files for dockers
      Docker run -it --rm \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 --label vip.service=requirements \
                 -w ${WIN}/tmp \
                 --entrypoint bash \
                 ${VIP_DOCKER_NOTEBOOK_IMAGE_NAME} \
                 ${WIN}${VIP_PROJECT_DIR_DOCK}/wrap ${WIN}${VIP_PROJECT_DIR_DOCK}/docker/update_requirements.bsh
      ;;
    *) 
      defaultify "${just_arg}" ${@+"${@}"} 
      ;;
  esac
}

#this is good enough to run simple commands until vsi submodule is setup
if ! command -v justify &> /dev/null; then function justify(){ caseify ${@+"${@}"};};fi

justify ${@+"${@}"}
