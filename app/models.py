from app import db

class News(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    title = db.Column(db.String(80))
    filename = db.Column(db.String(200))
    content = db.Column(db.String(1000))
    slug = db.Column(db.String(80))

class Country(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(80))
    filename = db.Column(db.String(200))
    latest = db.Column(db.String(1000))
    principal = db.Column(db.String(200))
    location = db.Column(db.String(200))
    heading = db.Column(db.String(80))
    about = db.Column(db.String(1000))
    slug = db.Column(db.String(80))
    
    def __repr__(self):
        return self.name
    

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