from flask import Flask
from flask.ext.login import LoginManager
from .models import User

app = Flask(__name__)
app.config.from_object('config')
app.debug = True

lm = LoginManager()
lm.init_app(app)

@lm.user_loader
def load_user(userid):
    user = User()
    return user

from app import views

def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix
        
app.jinja_env.globals.update(smart_truncate=smart_truncate)