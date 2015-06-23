from flask.ext.uploads import IMAGES
from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets import TextArea
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import Country, Category
from app import app

def countries_factory():
    return Country.query.all()
    
def categories_factory():
    return Category.query.all()

class LoginForm(Form):
    email = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class PageForm(Form):
    title = StringField('title', validators=[DataRequired()])
    body = StringField('body', validators=[DataRequired()],widget=TextArea())
    
class FileForm(Form):
    name = StringField('name', validators=[DataRequired()])
    file = FileField('file')

class NewsForm(Form):
    title = StringField('title', validators=[DataRequired()])
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    content = StringField('content', validators=[DataRequired()],widget=TextArea())
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)

class ResearchForm(Form):
    title = StringField('title', validators=[DataRequired()])
    file = FileField('file',validators=[FileAllowed(['pdf'], 'Papers must be formatted as .pdf')])
    image = FileField('image')
    body = StringField('content', validators=[Length(min=0, max=9000)],widget=TextArea()) 
    featured = BooleanField('featured', default=False)
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    
class StaffForm(Form):
    name = StringField('name', validators=[DataRequired()])
    title = StringField('title')
    institution = StringField('institution')
    sort_order = IntegerField('sort_order', [NumberRange(min=0, max=10)])
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    body = StringField('content', validators=[DataRequired()],widget=TextArea()) 
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True) 

class DatasetForm(Form):
    display = StringField('display', validators=[DataRequired()])
    short_display = StringField('short_display', validators=[DataRequired()])
    description = StringField('content', validators=[DataRequired()],widget=TextArea())
    unit = StringField('unit')
    source = StringField('source')
    content = FileField('content',validators=[FileAllowed(['csv'], 'Data must be formatted as .csv')])
    codebook = FileField('codebook',validators=[FileAllowed(['pdf'], 'Codebook must be formatted as .csv')])
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    category = QuerySelectField(query_factory=categories_factory,allow_blank=True) 
    
    def validate(self):
        rv = Form.validate(self)
        if self.fieldnames:
            required_fieldnames = ['id','year','majortopic','subtopic']
            #required_fieldnames = ['id','year','majortopic']
            for required_fieldname in required_fieldnames:
                if required_fieldname not in self.fieldnames:
                    self.content.errors.append('The required column "' + required_fieldname + '" was not found in the data you uploaded.')
        if len(self.content.errors) > 0:
            return False
        return True
    

class CountryForm(Form):
    name = StringField('name', validators=[DataRequired()])
    short_name = StringField('short_name', validators=[DataRequired()])
    principal = StringField('principal')
    location = StringField('location')
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    heading = StringField('heading', validators=[DataRequired()])
    about = StringField('content', validators=[DataRequired()],widget=TextArea())
    datasets_intro = StringField('datasets_intro', validators=[],widget=TextArea())
    embed_url = principal = StringField('embed_url')
    
class UserForm(Form):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    
class SlideForm(Form):
    heading = StringField('heading', validators=[DataRequired()])
    subheading = StringField('subheading', validators=[DataRequired()])
    link = StringField('link', validators=[DataRequired()])
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    active = BooleanField('active', default=False)
   
    