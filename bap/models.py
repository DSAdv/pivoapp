from datetime import datetime
from hashlib import md5
from flask_login import UserMixin
from sqlalchemy import func, and_
from werkzeug.security import generate_password_hash, check_password_hash

from bap import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class BeerPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(64), index=True)
    ean = db.Column(db.String(64), index=True, nullable=False)
    title = db.Column(db.String(256), index=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    ingredients = db.Column(db.Text)
    category_id = db.Column(db.String(64))
    description = db.Column(db.Text)
    nutrition_facts = db.Column(db.Text)
    slug = db.Column(db.String(64), nullable=False)
    web_url = db.Column(db.String(256))
    country = db.Column(db.String(64))
    weight = db.Column(db.Float)
    discount_diff = db.Column(db.Integer)
    is_discount = db.Column(db.Boolean)
    img_url = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @classmethod
    def get_by_date(cls, date: datetime.date, source: str = None):
        date_condition = func.date(cls.timestamp) == date
        condition = and_(cls.source == source, date_condition) if source else date_condition
        return cls.query.filter(condition).all()

    def __repr__(self):
        return '<BeerPosition {}:{}>'.format(self.title, self.source)
