from fabric.api import *
from fabric.colors import red
from fabric.contrib.files import exists
from fabric.contrib.console import confirm
from fabric.contrib.files import upload_template
from fabric.contrib.files import exists, append

env.hosts = ['192.168.1.106']




def install_elasticsearch():
    run("wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -")
    run("echo 'deb http://packages.elastic.co/elasticsearch/2.x/debian stable main' | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list")
    sudo('apt-get update')
    sudo('apt-get -y install elasticsearch')
    sudo('service elasticsearch restart')

def install_logstash():    
    run("echo 'deb http://packages.elasticsearch.org/logstash/1.5/debian stable main' | sudo tee -a /etc/apt/sources.list")
    sudo('apt-get update')
    sudo('apt-get -y install logstash')   
    sudo('touch /etc/logstash/conf.d/abc.conf')
    append(filename='/etc/logstash/conf.d/abc.conf', text="input {file {path => [ '/var/log/*.log']}}output {elasticsearch {hosts => ['localhost:9200']}stdout { codec => rubydebug }}", use_sudo=True)    
    sudo('service logstash start')

def install_kibana():
    sudo('apt-get -y install oracle-java8-installer')
    run("echo 'deb http://packages.elastic.co/kibana/4.4/debian stable main' | sudo tee -a /etc/apt/sources.list.d/kibana-4.4.x.list")    
    sudo('apt-get update')
    sudo('apt-get -y install kibana')
    sudo('service kibana start')
    
def final():
    install_elasticsearch()
    install_logstash()
    install_kibana()


# def elasticsearch():
#     run("curl -X POST 'http://localhost:9200/ctf/appointment/4' -d '{ 'ssn no': '123456' }'",warn_only=True))
    # echo("curl -X GET 'http://localhost:9200/ctf/appointment/2?pretty'")

    # http://localhost:9200/ctf/appointment/2?pretty
    # http://192.168.1.106:9200/ctf/appointment/1?pretty

# step : 1
# curl -X POST 'http://localhost:9200/ctf/appointment/1' -d '{ "token no": "123456" }'

# http://localhost:9222/ctf/appointment/1?pretty


# curl -X POST 'http://localhost:9222/tutorial/helloworld/1' -d '{ "message": "Hello World!" }'

# curl -X GET 'http://localhost:9200/tutorial/helloworld/1'
# curl -X GET 'http://localhost:9222/tutorial/helloworld/1?pretty'


# curl -X PUT 'localhost:9222/tutorial/helloworld/1?pretty' -d '