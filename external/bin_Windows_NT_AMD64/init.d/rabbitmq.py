from simple import Simple
from os import environ as env
from posixpath import join as pathjoin
import shlex
import os

if __name__=='__main__':
  env['RABBITMQ_BASE']=env['VIP_PROJECT_ROOT']
  env['RABBITMQ_LOG_BASE']=env['VIP_RABBITMQ_LOG_DIR']
  env['RABBITMQ_MNESIA_BASE']=env['VIP_RABBITMQ_MNESIA_BASE']
  env['HOMEDRIVE']=env['VIP_RABBITMQ_BASE_DRIVE']
  env['HOMEPATH']=env['VIP_RABBITMQ_BASE_PATH']
  env['RABBITMQ_PID_FILE']=env['VIP_RABBITMQ_PID_FILE']
  env['ERLANG_HOME']=env['VIP_RABBITMQ_ERLANG_HOME']
  
  if not os.path.exists(env['VIP_RABBITMQ_LOG_DIR']):
    os.mkdir(env['VIP_RABBITMQ_LOG_DIR']);
    
  Simple().run(['-o', pathjoin(env['VIP_RABBITMQ_LOG_DIR'], 'rabbitmq_out.log'),
                '-e', pathjoin(env['VIP_RABBITMQ_LOG_DIR'], 'rabbitmq_err.log'),
                '-p', pathjoin(env['VIP_INIT_DIR'], 'rabbitmq.pid'),
                'rabbitmq-server.bat'])
