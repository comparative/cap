from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class NewsForm(Form):
    title = StringField('title', validators=[DataRequired()])
    content = StringField('content', validators=[DataRequired()],widget=TextArea())