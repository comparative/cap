from app import db
from slugify import slugify

class News(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    title = db.Column(db.String(80))
    content = db.Column(db.String(500))
    slug = db.Column(db.String(500))

    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.slug = slugify(title)

class Countries(db.Model):

    country_id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(80))
    heading = db.Column(db.String(80))
    about = db.Column(db.String(500))
    slug = db.Column(db.String(80))

    def __init__(self, name):
        self.name = name
        self.slug = slugify(name)
    

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80))
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
        
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.name