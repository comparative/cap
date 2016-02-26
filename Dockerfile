FROM python:2.7

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y libpq-dev python-dev

RUN pip install configobj psycopg2 awesome-slugify cherrypy flask flask-login flask-mail flask-principal flask-security flask-script flask-sqlalchemy flask-uploads flask-wtf sqlalchemy-utils itsdangerous passlib tinys3 celery

#ADD . /var/www/cap

#EXPOSE 80

ADD start.sh /root/start.sh
RUN chmod +x /root/start.sh

CMD ["/root/start.sh"]