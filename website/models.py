from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Crime(db.Model):
    __tablename__ = 'crime'
    __table_args__ = {'extend_existing': True}  
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    location = db.Column(db.String(100))
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    crimes = db.relationship('Crime')

class Category(db.Model):
    cat_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    count = db.Column(db.Integer, default=0)
    
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    crime_reported = db.Column(db.String(10000))
    count = db.Column(db.Integer, default=0)
    emergency_number = db.Column(db.String(15))


# class Crime(db.Model):
#     __tablename__ = 'crime'
#     __table_args__ = {'extend_existing': True}  

#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text, nullable=False)
#     location = db.Column(db.String(100), nullable=False)
#     date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Crime {self.title}>'
