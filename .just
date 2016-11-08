#!/usr/bin/env false
#!This file should be sourced, NOT run

_just_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)

_just_services=($(\grep -E '^ *SERVICE_NAMES\+?=' "${_just_dir}/just" | \sed -E 's|.*=\((.*)\)|\1|'))

_just()
{
  COMPREPLY=()   # Array variable storing the possible completions.

  #More advanced feature, if one of the previous COMP_WORDS arguments contains
  #one of the commands that exec or consumes all the arguments, then use 
  #compgen -o default -- $2 instead

  #More advanced features, parse just for build_, start_, etc... commands and
  #customize the tab complete for those. Not necessary right now.

  local just_commands=($(\grep -E '^ +[a-z0-9\-]+\)|^ +[_a-z0-9\-]+\) *#' "${_just_dir}/just" | \sed -E 's|^ *([_a-z0-9\-]+)\).*|\1|'))

  local just_all_args=(vxl-debug telnet debug winpdb code rdm manage psql psqli)
  #TODO: Search for just_all_args commands in COMP_WORDS (COMP_CWORD) to determine
  #if I should use -o bashdefault

  local just_service

  for just_service in "${_just_services[@]}"; do
    if [ "$3" == "${just_service}" ]; then
      COMPREPLY=($(\compgen -W "${just_commands[*]} ${_just_services[*]}" -- $2))
      return 0
    fi
  done

  case "$3" in #switch statement based on previous argument
    copy-python|debug)
      COMPREPLY=($(\compgen -W "${_just_services[*]}" -- $2))
      return 0
      ;;
    start|stop|restart|quick-restart|build|clean|enter|kill|log|ip)
      COMPREPLY=($(\compgen -W "${just_commands[*]} ${_just_services[*]}" -- $2))
      return 0
      ;;
    django-load|django-dump|pg_restore)
      COMPREPLY=($(\compgen -f -- $2))
      return 0
      ;;
    *)
      COMPREPLY=($(\compgen -o bashdefault -W "${just_commands[*]}" -- $2))
      ;;
  esac

  return 0

}

alias just="\"${_just_dir}/just\""
complete -F _just just