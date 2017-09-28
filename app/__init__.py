import logging
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES, ALL
from celery import Celery
from HTMLParser import HTMLParser
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

app = Flask(__name__)
app.config.from_object('config')
app.debug = True
db = SQLAlchemy(app)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
#if not database_exists(engine.url):
#    create_database(engine.url)

lm = LoginManager()
lm.login_view = "login"
lm.init_app(app)

newsimages = UploadSet('newsimages', IMAGES)
countryimages = UploadSet('countryimages', IMAGES)
staffimages = UploadSet('staffimages', IMAGES)
researchfiles = UploadSet('researchfiles', 'pdf')
researchimages = UploadSet('researchimages', IMAGES)
adhocfiles = UploadSet('adhocfiles', ALL)
slideimages = UploadSet('slideimages', ALL)
codebookfiles = UploadSet('codebookfiles', ALL)
datasetfiles = UploadSet('datasetfiles', ALL)
topicsfiles = UploadSet('topicsfiles', ALL)
configure_uploads(app, (newsimages,countryimages,staffimages,researchfiles,researchimages,adhocfiles,slideimages,codebookfiles,datasetfiles,topicsfiles))

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

from app import views, models

def smart_truncate(content, length=100, suffix=' ...'):
    h = HTMLParser() 
    content = strip_tags(h.unescape(content))
    #content = content[3:-4]
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix
        
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


app.jinja_env.globals.update(smart_truncate=smart_truncate)

