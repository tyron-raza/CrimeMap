from app import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nid = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    crimes_reported = db.Column(db.Integer, default=0)
    password = db.Column(db.String(128), nullable=False)  # Increased size for hashed passwords
    
    # Relationship with Crime
    crimes = db.relationship('Crime', backref='user', lazy=True)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

class Crime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class FactChecker(db.Model):
    __tablename__ = 'fact_checkers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_admin = db.Column(db.Boolean, default=False)

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)