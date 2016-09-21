#!/usr/bin/env false
#!This file should be sourced, NOT run

_just_dir=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

_just()
{
  COMPREPLY=()   # Array variable storing the possible completions.

  #More advanced feature, if one of the previous COMP_WORDS arguments contains
  #one of the commands that exec or consumes all the arguments, then use 
  #compgen -o default -- $2 instead

  #More advanced features, parse just for build_, start_, etc... commands and
  #customize the tab complete for those. Not necessary right now.

  case "$3" in #switch statement based on previous argument
    start|stop|restart|quick-restart|build|clean|enter|kill|log|copy-python|ip)
      local just_services=($(\grep ^SERVICE_NAMES= ${_just_dir}/just | \sed -r 's|.*=\((.*)\)|\1|'))
      local just_multi_services=($(\grep ^MULTI_SERVICES= ${_just_dir}/just | \sed -r 's|.*=\((.*)\)|\1|'))

      COMPREPLY=($(\compgen -W "${just_services[*]} ${just_multi_services[*]}" -- $2))
      ;;
    django-load|django-dump|pg_restore)
      local just_commands=($(\grep -E '^ +[a-z0-9\-]+\)|^ +[_a-z0-9\-]+\) *#' ${_just_dir}/just | \sed -r 's|^ *([_a-z0-9\-]+)\).*|\1|'))
      COMPREPLY=($(\compgen -f -W "${just_commands[*]}" -- $2))
      ;;
    *)
      local just_commands=($(\grep -E '^ +[a-z0-9\-]+\)|^ +[_a-z0-9\-]+\) *#' ${_just_dir}/just | \sed -r 's|^ *([_a-z0-9\-]+)\).*|\1|'))
      COMPREPLY=($(\compgen -W "${just_commands[*]}" -- $2))
      ;;
  esac

  return 0

}

alias just=${_just_dir}/just
complete -F _just just