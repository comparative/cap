FROM python:2.7

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y libpq-dev python-dev

RUN pip install psycopg2 awesome-slugify cherrypy flask flask-login flask-mail flask-principal flask-security flask-script flask-sqlalchemy flask-uploads flask-wtf itsdangerous passlib