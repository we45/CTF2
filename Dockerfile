FROM ubuntu:16.04

RUN apt-get update && apt-get -y install software-properties-common python python-dev build-essential \
	python-distribute python-pip python-dev python libpq-dev libtiff5-dev libjpeg8-dev zlib1g-dev \
	libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk libxml2-dev \
	libxslt1-dev python-dev postgresql postgresql-contrib nginx

RUN pip install --upgrade pip && pip install BeautifulSoup==3.2.1 colorama==0.3.7 Django==1.8 \
	django-tastypie==0.13.3 Jinja2==2.8 MarkupSafe==0.23 nltk==3.2.1 Pillow==3.1.1 psycopg2==2.6.1 \
	python-dateutil==2.5.1 python-mimeparse==1.5.1 reportlab==3.3.0 requests==2.9.1 six==1.10.0 \
	termcolor==1.1.0 pycrypto==2.6.1 docopt==0.6.2 lxml==3.6.0 pytest gunicorn paho-mqtt==1.1 \
	selenium==2.53.6 python-owasp-zap-v2.4==0.0.8 elasticsearch==1.2.0

RUN mkdir -p /webapps/ctf2
COPY ctf2/hospital/hospital/ /webapps/ctf2/hospital/hospital/
COPY ctf2/hospital/ctf/ /webapps/ctf2/hospital/ctf/
COPY ctf2/hospital/manage.py /webapps/ctf2/hospital/
COPY gun_start /webapps/ctf2/hospital/
RUN chmod +x /webapps/ctf2/hospital/gun_start
RUN mkdir /webapps/ctf2/hospital/logs && touch /webapps/ctf2/hospital/logs/nginx-access.log && \
	touch /webapps/ctf2/hospital/logs/nginx-error.log

COPY sqldump.sql /
RUN rm -rf /etc/nginx/sites-available/*

COPY ctf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/ctf /etc/nginx/sites-enabled/
USER postgres
RUN  /etc/init.d/postgresql start && psql --command "ALTER USER postgres WITH PASSWORD 'StrongPassword';" &&  createdb -U postgres hospital_db && psql hospital_db < /sqldump.sql;
USER root
EXPOSE 5432 8000 80
ENV WEB_SERVER='localhost'
WORKDIR /webapps/ctf2/hospital/
COPY ssl-params.conf /etc/nginx/snippets/
COPY self-signed.conf /etc/nginx/snippets/
RUN openssl req -subj /CN=localhost/DC=localhost/DC=localdomain -new -newkey rsa:2048 -days "365" -nodes -x509 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
RUN openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
CMD service postgresql start && service nginx restart && /webapps/ctf2/hospital/gun_start
