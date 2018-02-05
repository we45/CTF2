from fabric.api import *
from jinja2 import Environment, FileSystemLoader
import vars
import os
from StringIO import StringIO
import psutil
from fabric.contrib.files import exists
#import fabric_gunicorn as gunicorn


env.hosts.append(vars.server_name)
env.user = 'root'
#env.password = 'cwasp'

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def install_mongo():
    local('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
    local('echo "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen" | sudo tee /etc/apt/sources.list.d/mongodb.list')
    local('apt-get update')
    local('apt-get install -y mongodb-org')
    

    
def install_everything():   
    install_mongo()



## MONGO Configs go HERE
    
def mongo_start():
    local('service mongod start')
    
def mongo_stop():
    with settings(warn_only = True):
        local('killall -q mongod')


def generate_mongo_ssl():
    if exists(vars.mongo_ssl_path):
        pass
    else:
        local('mkdir %s' % vars.mongo_ssl_path)
        local("openssl req -newkey rsa:2048 -new -x509 -days 365 -nodes -out %smongodb-cert.crt -keyout %smongodb-cert.key -subj '/C=US/ST=CA/O=Acme, Inc./CN=example.com'" % (vars.mongo_ssl_path, vars.mongo_ssl_path))
        with cd(vars.mongo_ssl_path):
            local("cat mongodb-cert.key mongodb-cert.crt > mongodb.pem")

def add_mongo_user():
    local('mongo admin --eval "db.addUser({\'user\':\'dummy2\',\'pwd\': \'dummy\',\'roles\':[\'userAdminAnyDatabase\']})"')
    
def check_mongo_user():
    output = local("mongo admin --eval \"db.system.users.find({'user':'dummy2'}).count()\"")
    list_out = output.splitlines()
    if len(list_out) == 3:
        if list_out[2] == '0':
            add_mongo_user()
            
def load_secure_conf_mongo():
    put('mongod.conf', '/home/cwasp/mongod.conf')    
            
def deploy_secure_mongo_conf():
    if exists('/home/cwasp/mongod.conf'):
        local('rm -rf /home/cwasp/mongod.conf')
        load_secure_conf_mongo()
    else:
        load_secure_conf_mongo()
        
def load_insecure_conf_mongo():
    put('mongod_insecure.conf', '/home/cwasp/mongod_insecure.conf')   
            
def deploy_insecure_mongo_conf():
    if exists('/home/cwasp/mongod_insecure.conf'):
        local('rm -rf /home/cwasp/mongod_insecure.conf')
        load_insecure_conf_mongo()
    else:
        load_insecure_conf_mongo()

def mongo_run_secure():
    mongo_stop()
    output = local('/usr/bin/mongod --fork --config /home/cwasp/mongod.conf', pty=False)
        

def mongo_run_insecure():
    mongo_stop()
    output = local('/usr/bin/mongod --fork --config /home/cwasp/mongod_insecure.conf', pty=False)




def run_secure_mongo_conf():
    mongo_stop()
    mongo_start()
    check_mongo_user()
    generate_mongo_ssl()
    deploy_secure_mongo_conf()
    mongo_run_secure()
    
def run_insecure_mongo():
    #mongo_stop()
    #mongo_start()
    deploy_insecure_mongo_conf()
    mongo_run_insecure()    
