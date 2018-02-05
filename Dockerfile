FROM jenkins
COPY ctf2_docker /var/jenkins_home/workspace/ctf2
RUN apt-get -y install python build-essential python-dev
RUN  apt-get -y install python-pip libpq-dev
RUN apt-get -y install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
RUN apt-get -y install -y libxml2-dev libxslt1-dev python-dev
RUN pip install virtualenv

