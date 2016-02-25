import ConfigParser
from StringIO import StringIO
from sqlalchemy import create_engine
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database

parser = ConfigParser.ConfigParser()
with open('/var/www/cap/config.py') as stream:
    fakefile = StringIO("[top]\n" + stream.read())
    parser.readfp(fakefile)
    
conn_str = parser.get('top', 'SQLALCHEMY_DATABASE_URI').strip("'")

engine = create_engine(conn_str)
if not database_exists(engine.url):
    create_database(engine.url)
