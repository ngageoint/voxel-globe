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
  fi

  if (( ${#running_containers[@]} == 0 )); then
    echo "No containers running"
    exit 1
  elif (( ${#running_containers[@]} > 1)); then
    for c in $(seq 1 ${#running_containers[@]}); do
      echo "$c - ${running_containers[$(($c-1))]}"
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
  ${DOCKER} exec -it ${container} bash
}

: ${CUDA_VERSION=$(/usr/local/cuda/bin/nvcc --version 2>/dev/null | tail -n 1 | awk '{print substr($(NF),2)}')} #'
: ${NVIDIA_VERSION=$(nvidia-smi -q 2>/dev/null | grep 'Driver Version' | awk -F': ' '{print $2}')} #'
: ${NVIDIA_VOLUME_NAME=nvidia_driver_${NVIDIA_VERSION}}

OS=$(uname)

RUN_ARGS=()
BUILD_ARGS=()

WIN= #Ming/cygwin hack
WINDOWS=0

if [ "${OS}" == "Linux" ]; then
  RUN_ARGS+=(-v ${NVIDIA_VOLUME_NAME}:/usr/local/nvidia:ro
             $(ls /dev/nvidia* | sed 's|^|--device |')
             -v /tmp/.X11-unix:/tmp/.X11-unix
             -e DISPLAY=${DISPLAY}
             -e VIP_INITIALIZE_DATABASE_CONFIRM=${VIP_INITIALIZE_DATABASE_CONFIRM})
else
  if [ "${OS}" != "Darwin" ]; then #Assume windows
    if (( ${BASH_VERSINFO[0]} > 3 )); then
      #export MSYS_NO_PATHCONV=1 #SHOULD work on the new git for windows, however winpty is still VERY broken
      #I just don't trust this MSYS_NO_PATHCONV option... wrote -v function instead. MORE things just break
      #in winpty :(
      DOCKER="winpty ${DOCKER}"
      WIN='/' #Ming/cygwin hack
    else
      WIN='/' #Ming/cygwin hack
    fi
    WINDOWS=1
  fi
  RUN_ARGS+=(-e VIP_OPENCL_INCLUDE_PATH=${WIN}/opt/AMDAPPSDK-3.0/include
             -e VIP_OPENCL_LIBRARY_FLAGS="-L${WIN}/opt/AMDAPPSDK-3.0/lib/x86_64/sdk -lOpenCL"
             -e VIP_OPENCL_LIBRARY_NAME=OpenCL
             -e VIP_OPENCL_LIBRARY_PATH=${WIN}/opt/AMDAPPSDK-3.0/lib/x86_64/sdk
             -e VIP_SKIP_SIFTGPU=1
             -e VIP_INITIALIZE_DATABASE_CONFIRM=${VIP_INITIALIZE_DATABASE_CONFIRM})
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

RUN_ARGS+=()

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

while (( $# > 0 )); do
  just_arg=$1
  shift 1

  # AFTER_ARGS=()

  # if (( $# > 0 )) && [ "$1" == "--" ]; then
  #   shift 1
  #   while (( $# > 0 )); do
  #     if [ "$1" == '**' ]; then
  #       shift 1
  #       break
  #     fi
  #     AFTER_ARGS+=($1)
  #     shift 1
  #   done
  # fi

  case ${just_arg} in
    build)
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
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_POSTGRES_IMAGE_NAME} \
                   -f ${CURDIR}/docker/postgresql.Dockerfile ${CURDIR}/docker
      ;; #"
    build_rabbitmq)
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_RABBITMQ_IMAGE_NAME} \
                   -f ${CURDIR}/docker/rabbitmq.Dockerfile ${CURDIR}/docker
      ;; #"
    build_celery)
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                   -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_CELERY_IMAGE_NAME} \
                   -f ${CURDIR}/docker/celery.Dockerfile ${CURDIR}/docker
      ;;
    build_httpd)
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                   -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_HTTPD_IMAGE_NAME} \
                   -f ${CURDIR}/docker/httpd.Dockerfile ${CURDIR}/docker
      ;;
    build_vxl)
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_VXL_IMAGE_NAME} \
                   -f ${CURDIR}/docker/vxl.Dockerfile ${CURDIR}/docker
      ;; #"
    build_flower)
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_FLOWER_IMAGE_NAME} \
                   -f ${CURDIR}/docker/flower.Dockerfile ${CURDIR}/docker
      ;; #"
    build_notebook)
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_COMMON_IMAGE_NAME} \
                   -f ${CURDIR}/docker/common.Dockerfile ${CURDIR}/docker
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                   -t ${VIP_DOCKER_NOTEBOOK_IMAGE_NAME} \
                   -f ${CURDIR}/docker/notebook.Dockerfile ${CURDIR}/docker
      ;;


    build_potree)
      ${DOCKER} build ${BUILD_ARGS[@]+"${BUILD_ARGS[@]}"} \
                      -t potree_builder \
                      -f ${CURDIR}/docker/build_potree.Dockerfile ${CURDIR}/docker
      ${DOCKER} run --rm -v "$(va "$1" /potree)" \
                    -e USER_ID=$(id -u) \
                    -e GROUP_ID=$(id -g) \
                    potree_builder
      shift 1
      ;; #"


    start)
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
      RUN_ARGS=(-v "$(va ${VIP_POSTGRESQL_DIR} ${VIP_POSTGRESQL_DIR_DOCK})")
      if [ "${VIP_POSTGRESQL_PUBLISH}" == "1" ]; then
        RUN_ARGS+=(-p ${VIP_POSTGRESQL_PORT}:${VIP_POSTGRESQL_PORT})
      fi
      ${DOCKER} run -d "${RUN_ARGS[@]}" \
                 --name ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 --label vip.service=${just_arg#*_} \
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 -e USER_ID=$(id -u) \
                 -e GROUP_ID=$(id -g) \
                 ${VIP_DOCKER_POSTGRES_IMAGE_NAME}
                 #-e POSTGRES_PASSWORD=${VIP_POSTGRESQL_PASSWORD}
      ;;
    start_rabbitmq)
      ${DOCKER} run -d -v "$(va ${VIP_RABBITMQ_VOLUME} ${VIP_RABBITMQ_DIR_DOCK})" \
                 --label vip.service=${just_arg#*_} \
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 --name ${VIP_DOCKER_RABBITMQ_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 ${VIP_DOCKER_RABBITMQ_IMAGE_NAME}
      ;;
    start_httpd)
      ${DOCKER} run -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_CONF_DIR} /usr/local/apache2/conf)" \
                 -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
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
      #TODO make start multiple nodes
      for i in ${!VIP_CELERY_NODES[@]}; do
        if [ "$(docker ps --filter=label=vip.service=celery --filter=label=vip.node=${VIP_CELERY_NODES[$i]} --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -q)" == "" ]; then
          ${DOCKER} run -d \
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
      ${DOCKER} run -d \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 --name ${VIP_DOCKER_FLOWER_CONTAINER_NAME} \
                 --net ${VIP_DOCKER_NETWORK} \
                 --label vip.service=${just_arg#*_} \
                 --label vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} \
                 -p ${VIP_FLOWER_PORT}:${VIP_FLOWER_PORT_DOCK} \
                 ${VIP_DOCKER_FLOWER_IMAGE_NAME}
      ;;
    start_notebook)
      ${DOCKER} run -d \
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


    stop)
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
      ${DOCKER} exec ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} gosu postgres pg_ctl stop || :
      echo
      ;;
    stop_rabbitmq)
      ${DOCKER} exec ${VIP_DOCKER_RABBITMQ_CONTAINER_NAME} rabbitmqctl stop || :
      ;;
    stop_httpd)
      ${DOCKER} exec ${VIP_DOCKER_HTTPD_CONTAINER_NAME} bash -c "${WIN}/opt/vip/wrap /usr/local/apache2/bin/httpd -k graceful-stop" || :
      ;;
    stop_celery)
      for i in ${!VIP_CELERY_NODES[@]}; do
        ${DOCKER} exec ${VIP_DOCKER_CELERY_CONTAINER_NAME}-$i bash -c 'cd /home/user && celery multi stop ${NODE_NAME}' || :
      done
      ;;
    stop_*)
      ${DOCKER} stop "$(docker ps --filter=label=vip.service=${just_arg#*_} --filter=label=vip.prefix=${VIP_DOCKER_CONTAINER_NAME_PREFIX} -q)" || :
      ;;


    wait)
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


    restart)
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
    quick-restart)
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
      ${DOCKER} exec ${VIP_DOCKER_HTTPD_CONTAINER_NAME} bash -c "/opt/vip/wrap /usr/local/apache2/bin/httpd -k graceful" || :
      ;;
    quick-restart_*)
      $0 stop ${just_arg#*_}
      $0 wait ${just_arg#*_}
      $0 start ${just_arg#*_}
      ;;


    kill)
      ${DOCKER} kill "${CONTAINER_NAMES[@]}"
      ;;


    push)
      for image_name in "${DOCKERHUB_IMAGE_NAMES[@]}"; do
        ${DOCKER} push ${image_name}
      done
      ;;


    pull)
      for image_name in "${DOCKERHUB_IMAGE_NAMES[@]}"; do
        ${DOCKER} pull ${image_name}
      done
      ;;


    clean)
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


    log)
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


    enter)
      if (( ${#@} > 0 )) && is_service "${@}"; then
        $0 enter_$1
        shift 1
      else
        enter_containers "${SERVICE_NAMES[@]}"
      fi
      ;;
    enter_*)
      enter_containers ${just_arg#*_}
      ;;


    vxl)
      if [ "${WINDOWS}" == "1" ]; then
        VXL_ARGS=(-e NUMBER_OF_PROCESSORS=2)
      fi
      ${DOCKER} run --rm \
                 -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -e BUILD_TYPE=${VIP_VXL_BUILD_TYPE} \
                 ${VXL_ARGS[@]+"${VXL_ARGS[@]}"} \
                 ${VIP_DOCKER_VXL_IMAGE_NAME}
      ;; #"
    network) # combine with volume, init or something
      if ! docker network inspect ${VIP_DOCKER_NETWORK} > /dev/null 2>&1; then
        ${DOCKER} network create ${VIP_DOCKER_NETWORK}
      fi
      ;;
    setup)
      $0 initialize-database collect-static
      ;; #"
    initialize-database)
      RUN_ARGS+=(-v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 --net ${VIP_DOCKER_NETWORK})

      mkdir -p ${VIP_IMAGE_DIR} ${VIP_STORAGE_DIR}

      #Start database, AND initialize for the first time probably
      $0 start postgresql

      #Initialize database
      ${DOCKER} run -it --rm "${RUN_ARGS[@]}" \
                    --net ${VIP_DOCKER_NETWORK} \
                    -e USER_ID=$(id -u) \
                    -e GROUP_ID=$(id -g) \
                    ${VIP_DOCKER_HTTPD_IMAGE_NAME} \
                    ${WIN}/opt/vip/data/initialize_database.py

      #Stop database
      $0 stop postgresql
      ;;
    collect-static)
      #deploy static file
      ${DOCKER} run --rm "${RUN_ARGS[@]}" \
                    --net ${VIP_DOCKER_NETWORK} \
                    -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                    -e USER_ID=$(id -u) \
                    -e GROUP_ID=$(id -g) \
                    ${VIP_DOCKER_HTTPD_IMAGE_NAME} \
                    ${WIN}${VIP_PROJECT_DIR_DOCK}/voxel_globe/static_common/deploy.py

      ;;
    reset-volume)
      if [ "${OS}" == "Linux" ]; then
        docker_create_volume ${NVIDIA_VOLUME_NAME}
        ${DOCKER} run --rm -v ${NVIDIA_VOLUME_NAME}:/nvidia -v /usr:/host:ro centos:7 bash -c \
          "mkdir /nvidia/{bin,lib64}; cp -a /host/bin/nvidia* /nvidia/bin && cp -ra /host/lib64/vdpau/* /host/lib64/nvidia/* /nvidia/lib64"
      fi

      for volume_name in ${VIP_RABBITMQ_VOLUME} ${VIP_VXL_VOLUME} ${VIP_NOTEBOOK_MPL_VOLUME}; do
        docker_create_volume ${volume_name}
      done

      if [ ! -d ${VIP_IMAGE_DIR} ]; then
        mkdir -p ${VIP_IMAGE_DIR}
        chmod 777 ${VIP_IMAGE_DIR}
      fi
      if [ ! -d ${VIP_STORAGE_DIR} ]; then
        mkdir -p ${VIP_STORAGE_DIR}
        chmod 777 ${VIP_STORAGE_DIR}
      fi
      ;;
    windows-volume)
      for volume_name in ${VIP_POSTGRESQL_DIR} ${VIP_STORAGE_DIR} ${VIP_IMAGE_DIR}; do
        docker_create_volume ${volume_name}
      done

      ${DOCKER} run --rm \
                 -v "$(va ${VIP_STORAGE_DIR} /storage)" \
                 -v "$(va ${VIP_IMAGE_DIR} /image)" \
                 debian:jessie chmod 777 ${WIN}/image ${WIN}/storage
      ;;
    dev)
      exec ${DOCKER} run -it --rm --net ${VIP_DOCKER_NETWORK} \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -e USER_ID=$(id -u) \
                 -e GROUP_ID=$(id -g) \
                 ${VIP_DOCKER_HTTPD_IMAGE_NAME} ${WIN}/opt/vip/dev.bsh
      ;;
    ps)
      ${DOCKER} ps -a --filter=name=$(echo ${CONTAINER_NAMES[@]} | sed 's| | --filter=name=|g')
      ;;
    telnet)
      exec ${DOCKER} run -it --rm --net ${VIP_DOCKER_NETWORK} jess/telnet ${@+"${@}"}
      ;; #"
    debug)
      exec ${DOCKER} run -it --rm --net ${VIP_DOCKER_NETWORK} \
                      -v "$(va ${VIP_RABBITMQ_VOLUME} /rabbitmq)" \
                      -v "$(va ${VIP_POSTGRESQL_DIR} /postgres)" \
                      -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                      -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                      -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                      -v "$(va ${VIP_VXL_SRC_DIR} ${VIP_VXL_SRC_DIR_DOCK})" \
                      -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                      chpio/gosu:jessie bash -c "groupadd user -g $(id -g) -o && \
                                        useradd -u $(id -u) -o --create-home --home-dir /home/user -g user user && \
                                        gosu user bash || bash"
      ;;
    manage)
      exec ${DOCKER} run -it --rm --net ${VIP_DOCKER_NETWORK} \
                 -v "$(va ${VIP_PROJECT_DIR} ${VIP_PROJECT_DIR_DOCK})" \
                 -v "$(va ${VIP_IMAGE_DIR} ${VIP_IMAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_STORAGE_DIR} ${VIP_STORAGE_DIR_DOCK})" \
                 -v "$(va ${VIP_VXL_VOLUME} ${VIP_VXL_DIR_DOCK})" \
                 -e VIP_IMAGE_DIR=${WIN}${VIP_IMAGE_DIR_DOCK} \
                 -e VIP_STORAGE_DIR=${WIN}${VIP_STORAGE_DIR_DOCK} \
                 -e USER_ID=$(id -u) \
                 -e GROUP_ID=$(id -g) \
                 -p ${VIP_START_MANAGE_PORT}:${VIP_START_MANAGE_DOCK_PORT} \
                 -w /opt/vip/voxel_globe \
                 ${VIP_DOCKER_HTTPD_IMAGE_NAME} ${WIN}/opt/vip/wrap python manage.py ${@+"${@}"}
      ;; #"
    psql)
      exec ${DOCKER} exec -i ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                         gosu ${VIP_POSTGRESQL_USER} psql ${@+"${@}"}
      ;; #"
    psqli) #interactive
      exec ${DOCKER} exec -it ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                         gosu ${VIP_POSTGRESQL_USER} psql ${@+"${@}"}
      ;; #"
    pg_dump)
      exec ${DOCKER} exec ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                         gosu ${VIP_POSTGRESQL_USER} pg_dump ${VIP_POSTGRESQL_DATABASE_NAME}
      ;;
    pg_restore)
      echo "Restoring ${VIP_POSTGRESQL_DATABASE_NAME} using $1"
      ${DOCKER} exec ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                     gosu ${VIP_POSTGRESQL_USER} \
                     dropdb ${VIP_POSTGRESQL_DATABASE_NAME} || :
      ${DOCKER} exec ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                     gosu ${VIP_POSTGRESQL_USER} \
                     createdb ${VIP_POSTGRESQL_DATABASE_NAME}
      exec ${DOCKER} exec -i ${VIP_DOCKER_POSTGRES_CONTAINER_NAME} \
                          gosu ${VIP_POSTGRESQL_USER} \
                          psql -d ${VIP_POSTGRESQL_DATABASE_NAME} < "$1"
      ;;
    *) echo "I don't understand ${just_arg}"; exit 1 ;;
  esac
done
