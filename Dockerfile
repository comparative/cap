FROM dockerfile/python
MAINTAINER Geoff Boyd <geoff.boyd@austin.utexas.com>
ADD . /var/www/cap
RUN pip install -r /var/www/quokka/requirements.txt