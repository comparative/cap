from flask.ext.uploads import IMAGES
from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, PasswordField, IntegerField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets import TextArea
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import Country, Category, Budgetcategory
from app import app

def countries_factory():
    return Country.query.all()
    
def categories_factory():
    return Category.query.all()
    
def budgetcategories_factory():
    return Budgetcategory.query.all()

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
    title = StringField('title')
    file = FileField('file',validators=[FileAllowed(['pdf'], 'Papers must be formatted as .pdf')])
    image = FileField('image')
    body = StringField('content', validators=[Length(min=0, max=9000)],widget=TextArea()) 
    featured = BooleanField('featured', default=False)
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    
class StaffForm(Form):
    name = StringField('name', validators=[DataRequired()])
    title = StringField('title')
    institution = StringField('institution')
    sort_order = IntegerField('sort_order', validators=[NumberRange(min=0, max=50)],default=0)
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    body = StringField('content', validators=[],widget=TextArea()) 
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True) 

class DatasetForm(Form):
    display = StringField('display', validators=[DataRequired()])
    short_display = StringField('short_display', validators=[DataRequired()])
    description = StringField('content', validators=[DataRequired()],widget=TextArea())
    unit = StringField('unit',validators=[DataRequired()])
    source = StringField('source')
    #content = FileField('content',validators=[FileAllowed(['csv'], 'Data must be formatted as .csv')])
    content = HiddenField("content")
    codebook = FileField('codebook',validators=[FileAllowed(['pdf'], 'Codebook must be formatted as .pdf')])
    topics = FileField('topics',validators=[FileAllowed(['csv'], 'Topics must be formatted as .csv')])
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    category = QuerySelectField(query_factory=categories_factory,allow_blank=True) 
    budgetcategory = QuerySelectField(query_factory=budgetcategories_factory,allow_blank=True) 
    aggregation_level = SelectField(u'Aggregation Level', choices=[('0', 'raw'), ('1', 'count'), ('2', 'percent')])
    
    def validate(self):
        rv = Form.validate(self)
        if self.fieldnames and self.aggregation_level > 0:
            if self.aggregation_level.data=='1' and 'count' not in self.fieldnames:
                self.aggregation_level.errors.append('To choose this option, your data needs a "count" column.')
            if self.aggregation_level.data=='2' and 'percent' not in self.fieldnames:
                self.aggregation_level.errors.append('To choose this option, your data needs a "percent" column.')                
        if len(self.aggregation_level.errors) > 0:
            self.content.data = None
        if self.topicsfieldnames:
            required_fieldnames = ['majorfunction','subfunction','shortname','longname']
            for required_fieldname in required_fieldnames:
                if required_fieldname not in self.topicsfieldnames:
                    self.topics.errors.append('The required column "' + required_fieldname + '" was not found in the data you uploaded.')
        if len(self.aggregation_level.errors) > 0 or len(self.topics.errors) > 0 or rv==False:
            return False
        return True

class StaticDatasetForm(Form):
    display = StringField('display', validators=[DataRequired()])
    short_display = StringField('short_display')
    description = StringField('content', validators=[DataRequired()],widget=TextArea())
    content = HiddenField("content")
    codebook = FileField('codebook',validators=[FileAllowed(['pdf'], 'Codebook must be formatted as .pdf')])
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    category = QuerySelectField(query_factory=categories_factory,allow_blank=True)

class CountryForm(Form):
    name = StringField('name', validators=[DataRequired()])
    short_name = StringField('short_name', validators=[])
    principal = StringField('principal')
    location = StringField('location')
    email = StringField('email')
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    heading = StringField('heading', validators=[DataRequired()])
    about = StringField('content', validators=[DataRequired()],widget=TextArea())
    datasets_intro = StringField('datasets_intro', validators=[],widget=TextArea())
    embed_url = principal = StringField('embed_url')
    budget_topics = StringField('budget_topics')
    sponsoring_institutions = StringField('sponsoring_institutions', validators=[],widget=TextArea())
    codebook = FileField('codebook',validators=[])
    
class UserForm(Form):
    name = StringField('name', validators=[])
    email = StringField('email', validators=[])
    password = StringField('password', validators=[DataRequired()])
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    
class SlideForm(Form):
    heading = StringField('heading', validators=[DataRequired()])
    subheading = StringField('subheading', validators=[DataRequired()])
    link = StringField('link', validators=[DataRequired()])
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    active = BooleanField('active', default=False)
   
    