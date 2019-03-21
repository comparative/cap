FROM python:latest

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y libpq-dev python-dev

RUN pip install cheroot configparser psycopg2 awesome-slugify flask-login flask-mail flask-principal flask-security flask-script flask-sqlalchemy flask-uploads flask-wtf sqlalchemy-utils itsdangerous passlib tinys3 celery oauth2client pyopenssl google-api-python-client

COPY . /cap

RUN mkdir /cap/datacache

ADD start.sh /root/start.sh
RUN chmod +x /root/start.sh

CMD ["/root/start.sh"]