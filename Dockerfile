#  DEVELOPMENT: 
#  docker run --name="web" -d -p 80:5000 -v /{wherever-you-cloned-it}/cap:/var/www/cap cap:web python /var/www/cap/wsgi.py
#  DEPLOY:
#  docker run -d -p 80:5000 cap:web

FROM python:2.7

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y libpq-dev python-dev

RUN pip install psycopg2 awesome-slugify cherrypy flask flask-login flask-mail flask-principal flask-security flask-script flask-sqlalchemy flask-uploads flask-wtf itsdangerous passlib

ADD . /var/www/cap

CMD ["python","/var/www/cap/wsgi.py"]