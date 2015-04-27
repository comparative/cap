from app import db
from sqlalchemy.dialects.postgresql import JSON
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
    description = db.Column(db.String(80))
    unit = db.Column(db.String(80))
    source = db.Column(db.String(80))
    content = db.Column(JSON)
    country_id = db.Column(db.Integer,db.ForeignKey('country.id'))
    country = db.relationship('Country',backref=db.backref('datasets', lazy='dynamic'))
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
    category = db.relationship('Category',backref=db.backref('categories', lazy='dynamic'))
    saved_date = db.Column(db.DateTime)

class Country(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(80))
    short_name = db.Column(db.String(80))
    filename = db.Column(db.String(200))
    principal = db.Column(db.String(200))
    location = db.Column(db.String(200))
    heading = db.Column(db.String(80))
    about = db.Column(db.String(9000))
    embed_url = db.Column(db.String(200))
    slug = db.Column(db.String(80))
    
    def __repr__(self):
        return self.name

class Category(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(80))
    
    def __repr__(self):
        return self.name 

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
    
    def __repr__(self):
        return self.slug
    