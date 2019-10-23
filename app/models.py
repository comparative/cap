from app import db
from sqlalchemy.dialects.postgresql import JSON,JSONB
from sqlalchemy.orm import deferred
import datetime

class Slide(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    heading = db.Column(db.String(80))
    subheading = db.Column(db.String(9000))
    link = db.Column(db.String(200))
    imagename = db.Column(db.String(200))
    active = db.Column(db.Boolean())

class Page(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.String(29000))
    slug = db.Column(db.String(80))
    
class File(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    filename = db.Column(db.String(200))
    slug = db.Column(db.String(80))

class News(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    title = db.Column(db.String(80))
    filename = db.Column(db.String(200))
    content = db.Column(db.String(9000))
    slug = db.Column(db.String(80))
    country_id = db.Column(db.Integer,db.ForeignKey('country.id'))
    country = db.relationship('Country',backref=db.backref('news', lazy='dynamic'))
    saved_date = db.Column(db.DateTime)

class Dataset(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    display = db.Column(db.String(80))
    short_display = db.Column(db.String(80))
    description = db.Column(db.String(9000))
    unit = db.Column(db.String(80))
    source = db.Column(db.String(80))
    content = deferred(db.Column(JSONB))
    country_id = db.Column(db.Integer,db.ForeignKey('country.id'))
    country = db.relationship('Country',backref=db.backref('datasets', lazy='dynamic'))
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
    category = db.relationship('Category',backref=db.backref('categories', lazy='dynamic'))
    saved_date = db.Column(db.DateTime)
    codebookfilename = db.Column(db.String(200))
    datasetfilename = db.Column(db.String(200))
    filters = db.Column(JSON)
    ready = db.Column(db.Boolean())
    stats_year_from = db.Column(db.Integer)
    stats_year_to = db.Column(db.Integer)
    stats_observations = db.Column(db.Integer)
    aggregation_level = db.Column(db.Integer)
    budget = db.Column(db.Boolean(),default=False)
    budgetcategory_id = db.Column(db.Integer,db.ForeignKey('budgetcategory.id'))
    budgetcategory = db.relationship('Budgetcategory',backref=db.backref('budget_categories', lazy='dynamic'))
    topics = db.Column(JSON)
    topicsfilename = db.Column(db.String(200))
    fieldnames = db.Column(JSON)
    measures = deferred(db.Column(JSONB))

class Staticdataset(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    display = db.Column(db.String(80))
    short_display = db.Column(db.String(80))
    description = db.Column(db.String(9000))
    country_id = db.Column(db.Integer,db.ForeignKey('country.id'))
    country = db.relationship('Country',backref=db.backref('staticdatasets', lazy='dynamic'))
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
    category = db.relationship('Category',backref=db.backref('staticcategories', lazy='dynamic'))
    saved_date = db.Column(db.DateTime)
    codebookfilename = db.Column(db.String(200))
    datasetfilename = db.Column(db.String(200))
    ready = db.Column(db.Boolean())

   
class Country(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(80))
    short_name = db.Column(db.String(80))
    filename = db.Column(db.String(200))
    principal = db.Column(db.String(200))
    email = db.Column(db.String(200))
    location = db.Column(db.String(200))
    heading = db.Column(db.String(80))
    about = db.Column(db.String(9000))
    embed_url = db.Column(db.String(200))
    slug = db.Column(db.String(80))
    datasets_intro = db.Column(db.String(9000))
    stats_series = db.Column(db.Integer)
    stats_year_from = db.Column(db.Integer)
    stats_year_to = db.Column(db.Integer)
    stats_observations = db.Column(db.Integer)
    sponsoring_institutions = db.Column(db.String(9000))
    codebookfilename = db.Column(db.String(200))
    
    
    def __repr__(self):
        return self.name

class Category(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(80))
    
    def __repr__(self):
        return self.name 

class Budgetcategory(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(80))
    
    def __repr__(self):
        return self.name


#class Aggregationlevel(db.Model):
#    
#    id = db.Column(db.Integer, primary_key=True)    
#    name = db.Column(db.String(80))
#    
#    def __repr__(self):
#        return self.name 


class Research(db.Model):

    id = db.Column(db.Integer, primary_key=True) 
    country_id = db.Column(db.Integer,db.ForeignKey('country.id'))
    country = db.relationship('Country',backref=db.backref('research', lazy='dynamic'))
    title = db.Column(db.String(80))
    filename = db.Column(db.String(200))
    imagename = db.Column(db.String(200))
    body = db.Column(db.String(9000))
    saved_date = db.Column(db.DateTime)
    featured = db.Column(db.Boolean())
    
    def __repr__(self):
        return self.title    

class Staff(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))  
    title = db.Column(db.String(80))
    institution = db.Column(db.String(80))
    filename = db.Column(db.String(200))
    body = db.Column(db.String(9000))
    country_id = db.Column(db.Integer,db.ForeignKey('country.id'))
    country = db.relationship('Country',backref=db.backref('staff', lazy='dynamic'))
    sort_order = db.Column(db.Integer)
    
    def __repr__(self):
        return self.title 
  

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80))
    country_id = db.Column(db.Integer,db.ForeignKey('country.id'))
    country = db.relationship('Country',backref=db.backref('users', lazy='dynamic'))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.name
                     
class Chart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True)
    options = db.Column(JSON)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    user = db.Column(db.String(36))
    unpinned = db.Column(db.Boolean(),default=False)
    def __repr__(self):
        return self.slug

class Major_topics:
    __tablename__ = 'major_topics'
    id = db.Column(db.Integer, primary_key=True)
    majorname = db.Column(db.String(255))
    shortname = db.Column(db.String(255))
    majortopic = db.Column(db.Integer)
    
class Sub_topics:
    __tablename__ = 'sub_topics'
    id = db.Column(db.Integer, primary_key=True)
    majortopic = db.Column(db.Integer)
    subtopic = db.Column(db.Integer)
    shortname = db.Column(db.String(50))
    longname = db.Column(db.String(255))