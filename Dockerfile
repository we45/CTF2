FROM ubuntu:14.04
RUN apt-get update
RUN apt-get -y install software-properties-common
RUN apt-get -y install python python-dev build-essential python-distribute
RUN apt-get update
RUN apt-get install -y python-pip python-dev python libpq-dev
RUN apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
RUN apt-get install -y libxml2-dev libxslt1-dev python-dev
RUN pip install --upgrade pip
RUN apt-get update
RUN pip install BeautifulSoup==3.2.1 colorama==0.3.7 Django==1.8 django-tastypie==0.13.3 Jinja2==2.8 MarkupSafe==0.23 nltk==3.2.1 paho-mqtt==1.1 Pillow==3.1.1 \
psycopg2==2.6.1 python-dateutil==2.5.1 python-mimeparse==1.5.1 reportlab==3.3.0 requests==2.9.1 selenium==2.53.6 six==1.10.0 \
termcolor==1.1.0 pycrypto==2.6.1 docopt==0.6.2 elasticsearch==1.2.0 \
lxml==3.6.0 pytest python-owasp-zap-v2.4==0.0.8 
RUN apt-get -y install postgresql postgresql-contrib
RUN pip install gunicorn
RUN apt-get -y install  nginx
RUN mkdir /webapps/

WORKDIR /webapps/

RUN groupadd --system webapps
RUN useradd --system --gid webapps --shell /bin/bash --home /webapps appman



RUN apt-get install -y ssh git-core

RUN git config --global core.compression 0
COPY ctf2/ /webapps/ctf2
COPY gun_start /webapps/ctf2/hospital/
RUN chmod u+x /webapps/ctf2/hospital/gun_start
RUN mkdir  /webapps/ctf2/hospital/logs
RUN touch /webapps/ctf2/hospital/logs/nginx-access.log
RUN touch /webapps/ctf2/hospital/logs/nginx-error.log
COPY sqldump.sql /
RUN rm -rf /etc/nginx/sites-available/*
COPY ctf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/ctf /etc/nginx/sites-enabled/
RUN nginx -t
RUN chown -R appman:webapps /webapps/
WORKDIR /webapps/ctf2/hospital/

USER postgres
RUN  /etc/init.d/postgresql start && psql --command "ALTER USER postgres WITH PASSWORD 'hegemony86';" &&  createdb -U postgres hospital_db && psql hospital_db < /sqldump.sql;
USER root
EXPOSE 5432 8000 80
ENV WEB_SERVER='localhost'
CMD service postgresql start && service nginx restart && ./gun_start







