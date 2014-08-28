# coding: utf8
"""
Author: Ilcwd
"""
import datetime
import os


# noinspection PyPackageRequirements
from fabric.api import put, cd, sudo, local, lcd, env
# noinspection PyPackageRequirements
from fabric.decorators import task, hosts
# noinspection PyPackageRequirements
from fabric.contrib import files


# server name
PROJECT_NAME = 'userpartition'
# git repository
GIT_REPO = "http://git.op.ksyun.com/kpserver/%s.git" % PROJECT_NAME
# configs needs to be replaced
REPLACE_CONFIGS = [
    'config.py'
]


# deploy hosts
lugu_userpartition = [
            '10.0.2.131',
            '10.0.2.132',
]


env.hosts = lugu_userpartition
env.user = 'tanzhongbei'


@hosts('0.0.0.0')
@task
def tar():
    svn_path = 'http://git.op.ksyun.com/tanzhongbei/userpartition.git'
    tmp_path = 'userpartition'
    svn_req = 'git clone "%s"' % svn_path
    local(svn_req)
    local('rm userpartition/.git* -fr')

    #local('rm %s -fr' % 'docsvr/test')
    local('rm %s -f' % 'userpartition/config.py')
        
    tar_file = 'userpartition%s.tar.gz' % datetime.datetime.now().strftime('%Y%m%d')
    tar_req = 'tar cvf %s %s' % (tar_file, tmp_path)
    local(tar_req)
    
    local('rm userpartition -fr')
    local('md5sum %s' % tar_file)


@task
def upload(frompath, topath):
    put(frompath, topath, use_sudo=True, mirror_local_mode=True)
    local('md5sum %s' % frompath)
    sudo('md5sum %s' % topath)


@task
def backup_update():    
    name = 'userpartition'
    src_path = '/data/apps/xserver/'
    app_path = src_path + name

    # stop
    with cd(app_path):
        sudo('%s stop' % './runuwsgi.sh')
        sudo('sleep 2')

    #copy
    tar_file = 'userpartition%s.tar.gz' % datetime.datetime.now().strftime('%Y%m%d')
    remote_temp_path = '~/userpartition_deploy/'

    sudo('mkdir -p %s' % remote_temp_path)

    put(tar_file, remote_temp_path, use_sudo=True, mirror_local_mode=True)

    #back_up
    #sudo('mkdir -p /data/bakapps/docsvr')
    bak_path = '/data/bakapps/userpartition' + datetime.datetime.now().strftime('%d%b%Y.%H%M%S')
    sudo('mv /data/apps/xserver/userpartition %s' % bak_path)    

    #move
    with cd(remote_temp_path):
        sudo('tar xf %s' % tar_file)
        sudo('mv %s %s' % (name, app_path))

    #fix config
    sudo('cp %s %s' % (bak_path + '/config.py', app_path + '/config.py'), warn_only=True)
    
    sudo('chmod +x %s' % app_path + '/runuwsgi.sh')    

    # start
    with cd(app_path):
        sudo('%s start' % './runuwsgi.sh')


