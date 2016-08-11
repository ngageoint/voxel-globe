#!/usr/bin/env bash
#J.U.S.T. - J.U.S.T. uncomplicated simple tasking

set -eu

CURDIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CURDIR}/vip.bsh

DOCKER=docker
: ${DRYRUN=0}
if [ "${DRYRUN}" != "0" ]; then
  DOCKER="echo docker"
fi
DOCKER_RUN="${DOCKER} run"
DOCKER_RUN_I="${DOCKER_RUN} -i"
DOCKER_RUN_IT="${DOCKER_RUN} -it"
DOCKER_EXEC="${DOCKER} exec"
DOCKER_EXEC_IT="${DOCKER_EXEC} -it"
DOCKER_BUILD="${DOCKER} build"

#List of images to push/pull
DOCKERHUB_IMAGE_NAMES=(${VIP_DOCKER_POSTGRES_IMAGE_NAME} ${VIP_DOCKER_RABBITMQ_IMAGE_NAME} ${VIP_DOCKER_CELERY_IMAGE_NAME} ${VIP_DOCKER_HTTPD_IMAGE_NAME} ${VIP_DOCKER_FLOWER_IMAGE_NAME} ${VIP_DOCKER_NOTEBOOK_IMAGE_NAME} ${VIP_DOCKER_VXL_IMAGE_NAME})

#These must have the same order
CONTAINER_NAMES=(${VIP_DOCKER_POSTGRES_CONTAINER_NAME} ${VIP_DOCKER_RABBITMQ_CONTAINER_NAME} ${VIP_DOCKER_HTTPD_CONTAINER_NAME} ${VIP_DOCKER_FLOWER_CONTAINER_NAME})
SERVICE_NAMES=(postgresql rabbitmq celery httpd flower)
MULTI_SERVICES=(celery)

COLORS=($'\e[31m' $'\e[32m' $'\e[33m' $'\e[35m' $'\e[36m' $'\e[37m')
COLOR_ERR=$'\e[3m'
NC=$'\e[0m'

for node in "${!VIP_CELERY_NODES[@]}"; do
  CONTAINER_NAMES+=(${VIP_DOCKER_CELERY_CONTAINER_NAME}-$node)
done

if [ "${VIP_DOCKER_USE_NOTEBOOK}" == 1 ]; then
  CONTAINER_NAMES+=(${VIP_DOCKER_NOTEBOOK_CONTAINER_NAME})
  SERVICE_NAMES+=(notebook)
fi

function docker_create_volume()
{
  if docker volume inspect "$1" > /dev/null 2>&1; then
    if [ "${VIP_DOCKER_DELETE_VOLUME_ON_RESET}" == "1" ]; then
      ${DOCKER} volume rm $1
    else
      return 0
    fi
  fi
  docker volume create --name $1
}

function enter_containers()
{
  local running_containers=()

  if (( ${#@} > 0 )); then
    for service_name in "${@}"; do
      running_containers+=($(docker ps --filter=label=vip.service=${service_name} --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} --format="{{.Names}}"))
    done
  else
    running_containers+=($(docker ps --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} --format="{{.Names}}"))
  fi

  if (( ${#running_containers[@]} == 0 )); then
    echo "No containers running"
    exit 1
  elif (( ${#running_containers[@]} > 1)); then
    for c in $(seq 1 ${#running_containers[@]}); do
      echo $c - ${running_containers[$(($c-1))]} $(docker inspect -f "{{.Config.Labels}}" ${running_containers[$(($c-1))]})
    done
    read -r -p "Choose which container to enter: " cid
    if (( $cid >= 1 )) && (( $cid <= ${#running_containers[@]} )); then
      container=${running_containers[$((${cid}-1))]}
    else
      echo "Invalid selection"
      exit 1
    fi
  else
    container=${running_containers[0]}
  fi
  ${DOCKER_EXEC_IT} ${container} bash
}

: ${CUDA_VERSION=$(/usr/local/cuda/bin/nvcc --version 2>/dev/null | tail -n 1 | awk '{print substr($(NF),2)}')}
: ${NVIDIA_VERSION=$(nvidia-smi -q 2>/dev/null | grep 'Driver Version' | awk -F': ' '{print $2}')}
: ${NVIDIA_VOLUME_NAME=nvidia_driver_${NVIDIA_VERSION}}

OS=$(uname)

RUN_ARGS=()

WIN= #Ming/cygwin hack
WINDOWS=0

if [ "${OS}" == "Linux" ]; then
  RUN_ARGS+=(-v ${NVIDIA_VOLUME_NAME}:/usr/local/nvidia:ro
             $(ls /dev/nvidia* | sed 's|^|--device |')
             -v /tmp/.X11-unix:/tmp/.X11-unix
             -e DISPLAY=${DISPLAY})
else
  if [ "${OS}" != "Darwin" ]; then #Assume windows
    WINDOWS=1
    #export MSYS_NO_PATHCONV=1 #SHOULD work on the new git for windows, however winpty is still VERY broken
    #I just don't trust this MSYS_NO_PATHCONV option... wrote va function instead. MORE things just break
    #in winpty :(
    WIN='/' #Ming/cygwin hack

    if which winpty > /dev/null 2>&1; then #mintty hack
      DOCKER_RUN_IT="winpty ${DOCKER_RUN_IT}"
      #Look into calling powershell instead
    elif [ "${TERM}" != "emacs" ]; then
      DOCKER_RUN_IT="cmd /s start ${DOCKER_RUN_I}"
    fi
  fi
  RUN_ARGS+=(-e VIP_OPENCL_INCLUDE_PATH=${WIN}/opt/AMDAPPSDK-3.0/include
             -e VIP_OPENCL_LIBRARY_FLAGS="-L${WIN}/opt/AMDAPPSDK-3.0/lib/x86_64/sdk -lOpenCL"
             -e VIP_OPENCL_LIBRARY_NAME=OpenCL
             -e VIP_OPENCL_LIBRARY_PATH=${WIN}/opt/AMDAPPSDK-3.0/lib/x86_64/sdk)
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

  if [ "${WINDOWS}" == "1" ]; then
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
     [ ! -d "${dir_name}" ]; then
     return 0 #TRUE!
  fi
   return 1 #False :(
}

if (( $# == 0 )); then
  exec $0 help
fi

while (( $# > 0 )); do
  just_arg=$1
  shift 1

  case ${just_arg} in
    build) # Build all the docker images. Only needs to be done if you did not pull or modified the dockerfiles
      export NOPULL=1 #disable auto pulling from ./just sync
      if (( ${#@} > 0 )) && is_service "${@}"; then
        while (( ${#@} > 0 )) && is_service "${@}"; do
          $0 build_$1
          shift 1
        done
      else
        $0 build_vxl build "${SERVICE_NAMES[@]}"
      fi

      ;;
    build_postgresql)
      ${DOCKER_BUILD} -t ${VIP_DOCKER_POSTGRES_IMAGE_NAME} \
                      -f ${CURDIR}/docker/postgresql.Dockerfile ${CURDIR}/docker
      ;;
    build_rabbitmq)
      ${DOCKER_BUILD} -t ${VIP_DOCKER_RABBITMQ_IMAGE_NAME} \
                      -f ${CURDIR}/docker/rabbitmq.Dockerfile ${CURDIR}/docker
      ;;
    build_celery)
      ${DOCKER_BUILD} -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                      -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      ${DOCKER_BUILD} -t ${VIP_DOCKER_CELERY_IMAGE_NAME} \
                      -f ${CURDIR}/docker/celery.Dockerfile ${CURDIR}/docker
      ;;
    build_httpd)
      ${DOCKER_BUILD} -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                      -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      ${DOCKER_BUILD} -t ${VIP_DOCKER_HTTPD_IMAGE_NAME} \
                      -f ${CURDIR}/docker/httpd.Dockerfile ${CURDIR}/docker
      ;;
    build_vxl)
      ${DOCKER_BUILD} -t ${VIP_DOCKER_VXL_IMAGE_NAME} \
                      -f ${CURDIR}/docker/vxl.Dockerfile ${CURDIR}/docker
      ;;
    build_flower)
      ${DOCKER_BUILD} -t ${VIP_DOCKER_FLOWER_IMAGE_NAME} \
                      -f ${CURDIR}/docker/flower.Dockerfile ${CURDIR}/docker
      ;;
    build_notebook)
      ${DOCKER_BUILD} -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                      -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      ${DOCKER_BUILD} -t ${VIP_DOCKER_NOTEBOOK_IMAGE_NAME} \
                      -f ${CURDIR}/docker/notebook.Dockerfile ${CURDIR}/docker
      ;;


    build_potree) #UNDOCUMENTED FEATURE build potree compiling image and compile potree. Argument is potree src dir
      ${DOCKER_BUILD} -t potree_builder \
                         -f ${CURDIR}/docker/build_potree.Dockerfile ${CURDIR}/docker
      ${DOCKER_RUN} --rm -v "$(va "$1" /potree)" \
                    -e USER_ID=$(id -u) \
                    -e GROUP_ID=$(id -g) \
                    potree_builder
      shift 1
      ;;
    build_winpdb) # UNDOCUMENTED FEATURE build winpdb
      ${DOCKER_BUILD} -t andyneff/winpdb \
                      -f ${CURDIR}/docker/winpdb.Dockerfile ${CURDIR}/docker
      ;;


    start) # Start all Voxel Globe containers. Optionally specify service names to only start specific containers
      if (( ${#@} > 0 )) && is_service "${@}"; then
        while (( ${#@} > 0 )) && is_service "${@}"; do
          container_ids=($(docker ps --filter=label=vip.service=$1 --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -q))
          if [ "${#container_ids[@]}" == "1" ]; then
            status=$(docker inspect --type=container -f "{{.State.Status}}" ${container_ids[0]})
          else
            status="none_or_multiple"
          fi
          if [ "${status}" == "running" ]; then
            echo "$1 is already running"
          else
            if [ "${status}" == "created" ]; then
              ${DOCKER} rm ${container_ids[0]}
            fi
            $0 clean_$1 start_$1
          fi
          shift 1
        done
      else #else start them ALL!
        $0 start ${SERVICE_NAMES[@]}
      fi
      ;;
    start_postgresql)
      ADD_ARGS=()
      if [ "${VIP_POSTGRESQL_PUBLISH}" == "1" ]; then
        ADD_ARGS+=(-p ${VIP_POSTGRESQL_PORT}:${VIP_POSTGRESQL_PORT})

      fi

      ${DOCKER_RUN} -d ${ADD_ARGS+"${ADD_ARGS[@]}"} \
                 -v "$(va ${VIP_POSTGRESQL_DIR} ${VIP_POSTGRESQL_DIR_DOCK})" \
                 --name ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 --label vip.service=${just_arg#*_} \
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 -e USER_ID=$(id -u) \
                 -e GROUP_ID=$(id -g) \
                 -p ${VIP_POSTGRESQL_PORT}:${VIP_POSTGRESQL_PORT_DOCK} \
                 ${VIP_DOCKER_POSTGRES_IMAGE_NAME}
                 #-e POSTGRES_PASSWORD=${VIP_POSTGRESQL_PASSWORD}
      ;;
    start_rabbitmq)
      ${DOCKER_RUN} -d -v "$(va ${VIP_RABBITMQ_VOLUME} ${VIP_RABBITMQ_DIR_DOCK})" \
                 --label vip.service=${just_arg#*_} \
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 --name ${VIP_DOCKER_RABBITMQ_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 ${VIP_DOCKER_RABBITMQ_IMAGE_NAME}
      ;;
    start_httpd)
      ${DOCKER_RUN} -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_CONF_DIR} /usr/local/apache2/conf)" \
                 -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -v "$(va ${VIP_HTTPD_SSL_VOLUME} ${VIP_HTTPD_SSL_DIR_DOCK})" \
                 --name ${VIP_DOCKER_HTTPD_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 -p ${VIP_HTTPD_SSL_PORT}:${VIP_HTTPD_SSL_PORT_DOCK} \
                 --label vip.service=${just_arg#*_} \
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 -e VIP_OPENCL_DEVICE=cpu0 \
                 -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                 -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                 -e USER_ID=$(id -u) \
                 -e GROUP_ID=$(id -g) \
                 ${VIP_DOCKER_HTTPD_IMAGE_NAME}
      ;;
    start_celery)
      for i in ${!VIP_CELERY_NODES[@]}; do
        if [ "$(docker ps --filter=label=vip.service=celery --filter=label=vip.node=${VIP_CELERY_NODES[$i]} --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -q)" == "" ]; then
          ${DOCKER_RUN} -d \
                   -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                   -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                   -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                   -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                   --label vip.service=${just_arg#*_} \
                   --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                   --label vip.node=${VIP_CELERY_NODES[$i]} \
                   -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                   -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                   -e USER_ID=$(id -u) \
                   -e GROUP_ID=$(id -g) \
                   -e NODE_NAME=${VIP_CELERY_NODES[$i]} \
                   --name ${VIP_DOCKER_CELERY_CONTAINER_NAME}-$i \
                   --net ${VIP_DOCKER_NETWORK} \
                   --hostname ${VIP_DOCKER_CELERY_CONTAINER_NAME}-$i \
                   ${VIP_DOCKER_CELERY_IMAGE_NAME}
        else
          echo "celery node ${VIP_CELERY_NODES[$i]} is already running"
        fi
      done
      ;;
    start_flower)
      ${DOCKER_RUN} -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 --name ${VIP_DOCKER_FLOWER_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 --label vip.service=${just_arg#*_} \
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 -p ${VIP_FLOWER_PORT}:${VIP_FLOWER_PORT_DOCK} \
                 ${VIP_DOCKER_FLOWER_IMAGE_NAME}
      ;;
    start_notebook)
      ${DOCKER_RUN} -d \
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
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 -e USER_ID=$(id -u) \
                 -e GROUP_ID=$(id -g) \
                 -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                 -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                 ${VIP_DOCKER_NOTEBOOK_IMAGE_NAME}
      ;;


    stop) # Stop all Voxel Globe containers. Optionally specify service names to only stop specific containers
      if (( ${#@} > 0 )) && is_service "${@}"; then
        while (( ${#@} > 0 )) && is_service "${@}"; do
          $0 stop_$1
          shift 1
        done
      else
        #stop them ALL! (in reverse order
        for (( idx=${#SERVICE_NAMES[@]}-1 ; idx>=0 ; idx-- )) ; do
          $0 stop "${SERVICE_NAMES[idx]}" || :
        done
      fi
      ;;
    stop_postgresql)
      # || : because 1) you WANT them all to run, and 2) pg_ctl doens't return 0
      ${DOCKER_EXEC} ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} gosu postgres pg_ctl stop || :
      echo
      ;;
    stop_rabbitmq)
      ${DOCKER_EXEC} ${VIP_DOCKER_RABBITMQ_CONTAINER_NAME} rabbitmqctl stop || :
      ;;
    stop_httpd)
      ${DOCKER_EXEC} ${VIP_DOCKER_HTTPD_CONTAINER_NAME} bash -c "${WIN}/opt/vip/wrap /usr/local/apache2/bin/httpd -k graceful-stop" || :
      ;;
    stop_celery)
      for i in ${!VIP_CELERY_NODES[@]}; do
        ${DOCKER_EXEC} ${VIP_DOCKER_CELERY_CONTAINER_NAME}-$i bash -c 'cd /home/user && celery multi stop ${NODE_NAME}' || :
      done
      ;;
    stop_*)
      ${DOCKER} stop "$(docker ps --filter=label=vip.service=${just_arg#*_} --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -q)" || :
      ;;


    wait) # Wait for all Voxel Globe containers to stop. Optionally specify service names to only wait on specific containers
      if (( ${#@} > 0 )) && is_service "${@}"; then
        while (( ${#@} > 0 )) && is_service "${@}"; do
          $0 wait_$1
          shift 1
        done
      else
        ${DOCKER} wait "${CONTAINER_NAMES[@]}"
      fi
      ;;
    wait_celery)
      for celery_node in $(docker ps -a --filter=name=${VIP_DOCKER_CELERY_CONTAINER_NAME} -q); do
        ${DOCKER} wait ${celery_node}
      done
      ;;
    wait_*)
      ${DOCKER} wait "$(docker ps -a --filter=label=vip.service=${just_arg#*_} --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -q)"
      ;;


    restart) # Restart all Voxel Globe containers. Optionally specify service names to only restart specific containers
      if (( ${#@} > 0 )) && is_service "${@}"; then
        while (( ${#@} > 0 )) && is_service "${@}"; do
          $0 restart_$1
          shift 1
        done
      else
        $0 stop wait start
      fi
      ;;
    restart_*)
      $0 stop ${just_arg#*_} wait ${just_arg#*_} start ${just_arg#*_}
      ;;
    quick-restart) # Same as 'restart', except httpd restarts faster in same container. Not useful for reloading environment
      if (( ${#@} > 0 )) && is_service "${@}"; then
        while (( ${#@} > 0 )) && is_service "${@}"; do
          $0 quick-restart_$1
          shift 1
        done
      else
        $0 quick-restart_httpd stop ${SERVICE_NAMES[@]/httpd} &
        ${DOCKER} wait ${CONTAINER_NAMES[@]/${VIP_DOCKER_HTTPD_CONTAINER_NAME}}
        $0 start ${SERVICE_NAMES[@]/httpd}
      fi
      ;;
    quick-restart_httpd)
      ${DOCKER_EXEC} ${VIP_DOCKER_HTTPD_CONTAINER_NAME} bash -c "/opt/vip/wrap /usr/local/apache2/bin/httpd -k graceful" || :
      ;;
    quick-restart_*)
      $0 stop ${just_arg#*_}
      $0 wait ${just_arg#*_}
      $0 start ${just_arg#*_}
      ;;


    kill) # Kill all Voxel Globe containers. Use this when 'stop' does not work (times out)
      ${DOCKER} kill "${CONTAINER_NAMES[@]}"
      ;;


    push) # Push docker images to docker hub
      for image_name in "${DOCKERHUB_IMAGE_NAMES[@]}"; do
        ${DOCKER} push ${image_name}
      done
      ;;


    pull) # Pull docker images from docker hub. Used this instead of 'build' if you are not modifying images yourself
      for image_name in "${DOCKERHUB_IMAGE_NAMES[@]}"; do
        ${DOCKER} pull ${image_name}
      done
      ;;


    clean) # Remove all dead Voxel Globe containers. Optionally specify service names to only clean specific containers
      if (( ${#@} > 0 )) && is_service "${@}"; then
        while (( ${#@} > 0 )) && is_service "${@}"; do
          $0 clean_$1
          shift 1
        done
      else
        for name in "${SERVICE_NAMES[@]}"; do
          $0 clean_$name
        done
      fi
      ;;
    clean_*)
      for container_id in $(docker ps -a --filter=label=vip.service=${just_arg#*_} --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -q); do
        if [ "$(docker inspect -f '{{.State.Status}}' --type container ${container_id})" != "running" ]; then
          ${DOCKER} rm ${container_id}
        fi
      done
      ;;


    log) # Show logs from all Voxel Globe containers. Optionally specify service names to only start specific containers
      function kill_logs()
      {
        for pid in "${LOG_PIDS[@]}"; do
          if [ "${WINDOWS}" == "1" ]; then
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

      function start_log_tail()
      { #container_name color
        echo $2 $1 ${NC}

        if [ "${WINDOWS}" == "1" ]; then
          WINDOWS_DELAY="sleep 2"
          #Added sleep for 2 seconds for windows. Ctrl+C actually kills the 
          #docker logs in windows, meaning the children kill is less then 
          #necessary. But at least this way I have TWO seconds to go from the
          #local children= line to the first kill. So should be good
        else
          WINDOWS_DELAY=:
        fi

        if [ "${WINDOWS}" == "1" ] && (( ${BASH_VERSINFO[0]} < 4 )); then
          bash -c "while :; do \
                     docker logs -f --tail=20 $1 2>&1 | \
                       sed -u 's|^|$2|' | sed -u 's|$|${NC}|'; \
                     ${WINDOWS_DELAY}; \
                     first_message=echo; "' \
                     while [ "$(docker inspect --type=container -f {{.State.Status}} '$1')" != "running" ]; do '" \
                       \$first_message Waiting for $1 to start...; \
                       first_message=: ;\
                       sleep 0.5; \
                     done
                   done"&
          LOG_PIDS+=($!)
        else
          bash -c "while :; do \
                     docker logs -f --tail=20 $1 \
                       2> >(sed -u 's|^|${COLOR_ERR}$2|' | sed -u 's|$|${NC}|') \
                       1> >(sed -u 's|^|$2|' | sed -u 's|$|${NC}|'); \
                     ${WINDOWS_DELAY}; \
                     first_message=echo; "' \
                     while [ "$(docker inspect --type=container -f {{.State.Status}} '$1')" != "running" ]; do '" \
                       \$first_message Waiting for $1 to start...; \
                       first_message=: ;\
                       sleep 0.5; \
                     done
                   done"&
          LOG_PIDS+=($!)
        fi
      }

      trap kill_logs INT
      LOG_PIDS=()

      if (( ${#@} > 0 )) && is_service "${@}"; then
        i=1
        while (( ${#@} > 0 )) && is_service "${@}"; do
          container_ids=($(docker ps --filter=label=vip.service=$1 --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -aq --format={{.Names}}))
          for j in "${!container_ids[@]}"; do
            start_log_tail ${container_ids[j]} ${COLORS[$(($i%${#COLORS[@]}))]}
          done
          i=$((i+1))
          shift 1
        done
      else
        for i in "${!CONTAINER_NAMES[@]}"; do
          start_log_tail ${CONTAINER_NAMES[$i]} ${COLORS[$(($i%${#COLORS[@]}))]}
        done
      fi

      wait "${LOG_PIDS[@]}" 2>/dev/null
      trap - INT
      ;;


    enter) # Enter a running container and start an interactive bash session. If you do not specify a specific service, a list will be supplied
      if (( ${#@} > 0 )) && is_service "${@}"; then
        $0 enter_$1
        shift 1
      else
        enter_containers
      fi
      ;;
    enter_*)
      enter_containers ${just_arg#*_}
      ;;


    vxl) # Compile external/vxl_src in a docker for use by the other containers
      if [ "${WINDOWS}" == "1" ]; then
        VXL_ARGS=(-e NUMBER_OF_PROCESSORS=2)
      fi
      ${DOCKER_RUN_IT} --rm \
                 -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -e BUILD_TYPE=${VIP_VXL_BUILD_TYPE} \
                 ${VXL_ARGS[@]+"${VXL_ARGS[@]}"} \
                 ${VIP_DOCKER_VXL_IMAGE_NAME}
      ;;
    vxl-cmake) # Force Cmake to re-run on the vxl build
      ${DOCKER_RUN_IT} --rm \
                 -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -e BUILD_TYPE=${VIP_VXL_BUILD_TYPE} \
                 -w ${WIN}${VIP_VXL_DIR_DOCK}/build/${VIP_VXL_BUILD_TYPE} \
                 ${VIP_DOCKER_VXL_IMAGE_NAME} cmake .
      ;;
    vxl-debug) # Enter the vxl build docker for easier debugging
      ${DOCKER_RUN_IT} --rm \
                 -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -e BUILD_TYPE=${VIP_VXL_BUILD_TYPE} \
                 ${VIP_DOCKER_VXL_IMAGE_NAME} bash
      ;;
    setup) # WARNING: this will WIPE an existing database. Runs 'network', 'initialize-database', and 'collect-static' for you.
      $0 network initialize-database collect-static
      ;;
    network) #Initialize Voxel Globe Docker network, only needs to be done once
      if ! docker network inspect ${VIP_DOCKER_NETWORK} > /dev/null 2>&1; then
        ${DOCKER} network create ${VIP_DOCKER_NETWORK}
      fi
      ;;
    initialize-database) # WARNING: this will WIPE an existing database. Initialize database. Must do this before using Django
      #Start database, AND initialize for the first time probably
      stop_database=0
      if [ "$(docker inspect --type=container -f "{{.State.Status}}" ${VIP_DOCKER_POSTGRES_CONTAINER_NAME})" != "running" ]; then
        stop_database=1
        $0 start postgresql
      fi

      #Initialize database
      ${DOCKER_RUN_IT} --rm \
                    --net ${VIP_DOCKER_NETWORK} \
                    -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                    -e USER_ID=$(id -u) \
                    -e GROUP_ID=$(id -g) \
                    ${VIP_DOCKER_HTTPD_IMAGE_NAME} \
                    ${WIN}/opt/vip/data/initialize_database.py

      if [ "${stop_database}" == "1" ]; then
        #Stop database
        $0 stop postgresql
      fi
      ;;
    collect-static) # Prepare and collect static files for use in httpd and test webserver. Must be done every time static libraries are changed
      ${DOCKER_RUN} --rm \
                    --net ${VIP_DOCKER_NETWORK} \
                    -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                    -e USER_ID=$(id -u) \
                    -e GROUP_ID=$(id -g) \
                    ${VIP_DOCKER_HTTPD_IMAGE_NAME} \
                    ${WIN}${VIP_PROJECT_DIR_DOCK}/voxel_globe/static_common/deploy.py

      ;;
    reset-volume) # WARNING: This will probably DESTROY and internal docker volumes. Create initial storage volumes
      if [ "${OS}" == "Linux" ]; then
        nvidia_libraries=('libGL\.so' 'libEGL\.so' 'libGLES.*\.so' 
                          'libnvcuvid\.so' 'libnvidia.*\.so' 'libOpenCL\.so'
                          'libglx\.so')
        #Simple (not extended) regular expressions

        nvidia_bins=(nvidia-xconfig start-nvidia-persistenced stop-nvidia-persistenced
                     nvidia-settings nvidia-detector nvidia-cuda-mps-server nvidia-smi
                     nvidia-persistenced nvidia-debugdump nvidia-cuda-mps-control 
                     nvidia-bug-report.sh nvidia_does_not_exist)

        if [ "$(docker inspect --type=container -f "{{.State.Status}}" ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer 2>/dev/null)" == "running" ]; then
          docker kill ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer
        fi

        if docker inspect --type=container -f "{{.State.Status}}" ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer > /dev/null 2>&1; then
          docker rm ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer
        fi

        docker_create_volume ${NVIDIA_VOLUME_NAME}

        docker run -d --name ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer \
                   -v ${NVIDIA_VOLUME_NAME}:/nvidia \
                   debian:jessie bash -c "while : ; do sleep 10; done"

        docker exec ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer mkdir -p /nvidia/{bin,lib64}

        #These cps are REALLY slow. Takes like 10 SECONDS! :(
        for nvidia_library in "${nvidia_libraries[@]}"; do
          for match in $(lwhich64 "$nvidia_library"); do
            docker cp "${match}" ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer:/nvidia/lib64
          done
        done

        for nvidia_bin in "${nvidia_bins[@]}"; do
          match=$(which ${nvidia_bin} 2>/dev/null || :)
          if [ "${match}" != "" ]; then
            docker cp "${match}" ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer:/nvidia/bin
          fi
        done

        docker kill ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer
        docker rm ${VIP_DOCKER_CONTAINER_NAME_PREFIX}-transfer
      fi

      for volume_name in ${VIP_RABBITMQ_VOLUME} ${VIP_VXL_VOLUME} ${VIP_NOTEBOOK_MPL_VOLUME} ${VIP_HTTPD_SSL_VOLUME}; do
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

      ${DOCKER_RUN} --rm \
                 -v "$(va ${VIP_NOTEBOOK_MPL_VOLUME} /matplotlib)" \
                 -v "$(va ${VIP_HTTPD_SSL_VOLUME} /ssl)" \
                 debian:jessie bash -c 'chmod 777 /matplotlib; chmod 755 /ssl'

      ;;
    windows-volume) # WARNING: This will probably DESTROY IMAGES and STORAGE internal docker volumes!!! Create initial storage volumes for windows
      for volume_name in ${VIP_POSTGRESQL_DIR} ${VIP_STORAGE_DIR} ${VIP_IMAGE_DIR}; do
        docker_create_volume ${volume_name}
      done

      ${DOCKER_RUN} --rm \
                 -v "$(va ${VIP_STORAGE_DIR} /storage)" \
                 -v "$(va ${VIP_IMAGE_DIR} /image)" \
                 debian:jessie chmod 777 ${WIN}/image ${WIN}/storage
      ;;
    dev) # Conveniently run developer tasks, like migrating database, etc...
      exec ${DOCKER_RUN_IT} --rm --net ${VIP_DOCKER_NETWORK} \
                         -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                         -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                         -e USER_ID=$(id -u) \
                         -e GROUP_ID=$(id -g) \
                         -e VIP_OS=${VIP_OS} \
                         --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                         ${VIP_DOCKER_HTTPD_IMAGE_NAME} ${WIN}/opt/vip/dev.bsh
      ;;
    sync) # Helper for the dev that runs through all possible sync operations. Useful to call after any git merge "J.U.S.T. in case"
      $0 stop pull vxl-cmake vxl collect-static start postgresql 
      $0 manage migrate
      $0 stop postgresql
      #git submodule update?
      echo 
      echo "You can run '$0 start' now..."
      ;;
    ps) # List all Voxel Globe containers and their statuses
      ${DOCKER} ps -a --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX}
      ;;
    telnet) # Start a telnet docker. Useful for python debuggers that need a telnet connection. All additional arguments are sent to telnet command
      exec ${DOCKER_RUN_IT} --rm --net ${VIP_DOCKER_NETWORK} \
                         --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                         jess/telnet ${@+"${@}"}
      ;;
    debug) # Start and enter a special debug docker. Mainly useful in accessing docker volumes. Type 'exit 1' to become root
      #TODO Add nvidia volume
      OTHER_ARGS=()
      if [ "$(uname)" == "Linux" ]; then
        OTHER_ARGS+=(-v /tmp/.X11-unix:/tmp/.X11-unix)
      fi
      exec ${DOCKER_RUN_IT} --rm --net ${VIP_DOCKER_NETWORK} \
                      -v "$(va ${VIP_RABBITMQ_VOLUME} /rabbitmq)" \
                      -v "$(va ${VIP_POSTGRESQL_DIR} /postgres)" \
                      -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                      -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                      -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                      -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                      -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                      -v "$(va ${NVIDIA_VOLUME_NAME} /nvidia)" \
                      -v "$(va ${VIP_NOTEBOOK_MPL_VOLUME} ${VIP_NOTEBOOK_MPL_DIR_DOCK})" \
                      -v "$(va ${VIP_HTTPD_SSL_VOLUME} ${VIP_HTTPD_SSL_DIR_DOCK})" \
                      -e DISPLAY=${DISPLAY+""} \
                      --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                      ${OTHER_ARGS[@]+"${OTHER_ARGS[@]}"} \
                      chpio/gosu:jessie bash -c "groupadd user -g $(id -g) -o && \
                                        useradd -u $(id -u) -o --create-home --home-dir /home/user -g user user && \
                                        gosu user bash || bash"
      ;;
    winpdb) # Start winpdb. Useful for graphically debugging python remotely. All additional arguments are sent to winpdb
      if [ "$(uname)" == "Linux" ]; then
        exec ${DOCKER_RUN_IT} --rm --net ${VIP_DOCKER_NETWORK} \
                       -v /tmp/.X11-unix:/tmp/.X11-unix \
                       -e DISPLAY=${DISPLAY} \
                       -e USER_ID=$(id -u) \
                       -e GROUP_ID=$(id -g) \
                       andyneff/winpdb winpdb ${@+"${@}"}
      fi
      ;;
    runserver) # Runs runserver
      exec ${DOCKER_RUN_IT} --rm --net ${VIP_DOCKER_NETWORK} \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 --label vip.service=manage \
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                 -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                 -e USER_ID=$(id -u) \
                 -e GROUP_ID=$(id -g) \
                 -p ${VIP_START_MANAGE_PORT}:${VIP_START_MANAGE_DOCK_PORT} \
                 -w ${WIN}/opt/vip/voxel_globe \
                 ${VIP_DOCKER_CELERY_IMAGE_NAME} ${WIN}/opt/vip/wrap python manage.py runserver 0.0.0.0:${VIP_START_MANAGE_DOCK_PORT}
      ;;
    manage) # Run django manage.py script. All additional arguments are sent to manage.py
      exec ${DOCKER_RUN_IT} --rm --net ${VIP_DOCKER_NETWORK} \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 --label vip.service=manage \
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                 -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                 -e USER_ID=$(id -u) \
                 -e GROUP_ID=$(id -g) \
                 -w ${WIN}/opt/vip/voxel_globe \
                 ${VIP_DOCKER_CELERY_IMAGE_NAME} ${WIN}/opt/vip/wrap python manage.py ${@+"${@}"}
      ;;
    ip) # Helper to print out the name and ip address of a service. No argument will list all ips, else an argument of service name, or manage
      if [ "$#" == "0" ]; then
        containers="$(docker ps --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -q)"
      else
        containers="$(docker ps --filter=label=vip.service=$1 \
                                --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -q)"
        shift 1
      fi
      docker inspect --format="{{.Name}}"$'\t'"{{.NetworkSettings.Networks.${VIP_DOCKER_NETWORK}.IPAddress}}" \
                     ${containers}
      ;;

    django-password) # Resets the django password. Applied at next database initialize
      ${DOCKER_RUN_IT} --rm -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                       -e USER_ID=$(id -u) \
                       -e GROUP_ID=$(id -g) \
                       ${VIP_DOCKER_HTTPD_IMAGE_NAME} \
                       /opt/vip/wrap python /opt/vip/shadow/make_django_password.py
      ;;
    psql) # Run psql in postgresql container in non tty mode. Useful for piping files to psql
      exec ${DOCKER_EXEC} -i ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                         gosu ${VIP_POSTGRESQL_USER} psql ${@+"${@}"}
      ;;
    psqli) # Run psql in postgresql container in tty mode. Useful for interactive session
      exec ${DOCKER_EXEC_IT} ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                         gosu ${VIP_POSTGRESQL_USER} psql ${@+"${@}"}
      ;;
    pg_dump) # Dump database to stdout. Usage ./just pg_dump > my_database.sql
      exec ${DOCKER_EXEC} ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                         gosu ${VIP_POSTGRESQL_USER} pg_dump ${VIP_POSTGRESQL_DATABASE_NAME}
      ;;
    pg_restore) # Drops the database, and reads in from file specified as next argument. Usage ./just pg_restore my_database.sql
      echo "Restoring ${VIP_POSTGRESQL_DATABASE_NAME} using $1"
      ${DOCKER_EXEC} ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                     gosu ${VIP_POSTGRESQL_USER} \
                     dropdb ${VIP_POSTGRESQL_DATABASE_NAME} || :
      ${DOCKER_EXEC} ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                     gosu ${VIP_POSTGRESQL_USER} \
                     createdb ${VIP_POSTGRESQL_DATABASE_NAME}
      ${DOCKER_EXEC} -i ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                     gosu ${VIP_POSTGRESQL_USER} \
                     psql -d ${VIP_POSTGRESQL_DATABASE_NAME} < "$1"
      shift 1
      ;;
    le-cert) # Runs let's encrypt, registering a certificate against $1
      ${DOCKER_EXEC} ${VIP_DOCKER_HTTPD_CONTAINER_NAME} ${WIN}/opt/vip/wrap \
                     ./conf/monkey_certbot certonly -n --apache \
                     --domains=$1 --apache-server-root=${WIN}/usr/local/apache2 \
                     --apache-handle-sites ${WIN}/usr/local/apache2/conf \
                     --agree-tos --email ${VIP_ADMIN_EMAIL} \
                     --apache-challenge-location ${WIN}/tmp
      #I don't know WHY I need to do this, but oh well...
      ${DOCKER_EXEC} ${VIP_DOCKER_HTTPD_CONTAINER_NAME} \
                     chmod -R 755 ${WIN}${VIP_HTTPD_SSL_DIR_DOCK}
      shift 1
      ;;
    le-renew) #Renews let's encrypt certificate
      ${DOCKER_EXEC} ${VIP_DOCKER_HTTPD_CONTAINER_NAME} ${WIN}/opt/vip/wrap \
                     ./conf/monkey_certbot renew -n --apache
      #I don't know WHY I need to do this, but oh well...
      ${DOCKER_EXEC} ${VIP_DOCKER_HTTPD_CONTAINER_NAME} \
                     chmod -R 755 ${WIN}${VIP_HTTPD_SSL_DIR_DOCK}
      ;;
    help) # Please see 'help' to see what this command does
      echo "List of possible J.U.S.T. commands:"
      echo "-----------------------------------"
      cols=$(tput cols)
      indent=21
      grep -E '^ +[a-z\-]+\)|^ +[_a-z\-]+\) *#' $0 | sed -r 's| *([_a-z-]*)\) *#? *(.*)|\1 --- \2|' \
      | awk -F '---' '
       { printf "%-'$(($indent-1))'s ", $1
        n = split($2,x," ")
        len = '${indent}'
        for(i=1;i<=n;i++){
         if(len+length(x[i])>='$(tput cols)'){printf("\n%'$indent's", ""); len = '${indent}'}
         printf "%s ",x[i]
         len += 1+length(x[i])
        }
        printf "\n"
      }' #c/o http://unix.stackexchange.com/a/280205/123413
      ;;
    *) echo "I don't understand ${just_arg}"; exit 1 ;;
  esac
done
