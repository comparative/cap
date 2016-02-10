import logging
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES, ALL
from celery import Celery
app = Flask(__name__)
app.config.from_object('config')
app.debug = True
db = SQLAlchemy(app)

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

def smart_truncate(content, length=100, suffix='...'):
    content = content[3:-4]
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix
        
app.jinja_env.globals.update(smart_truncate=smart_truncate)

