# USAGE: docker run -d -p 80:5000 -v /var/www/cap:/var/www/cap IMAGE 

FROM dockerfile/python

VOLUME  ["/var/www/cap", "/var/www/cap"]

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y libpq-dev python-dev && apt-get install -y python-psycopg2

RUN pip install awesome-slugify cherrypy flask flask-login flask-mail flask-principal flask-security flask-script flask-sqlalchemy flask-uploads flask-wtf itsdangerous passlib

CMD ["/usr/bin/python","/var/www/cap/wsgi.py"]