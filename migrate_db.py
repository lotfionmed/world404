from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '5e7eb9a6c28b4b3f8f0c1d2e4a6b8c0d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photogram.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_photo = db.Column(db.String(255), default='uploads/default_profile.png')
    bio = db.Column(db.String(500))
    
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    
    followers = db.relationship(
        'Follow', 
        foreign_keys=[Follow.followed_id], 
        backref='followed', 
        lazy='dynamic'
    )
    following = db.relationship(
        'Follow', 
        foreign_keys=[Follow.follower_id], 
        backref='follower', 
        lazy='dynamic'
    )

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('authored_comments', lazy=True))

def migrate_database():
    # Remove existing database
    db_path = os.path.join(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Recreate database with new schema
    with app.app_context():
        db.create_all()
        print("Database migrated successfully!")

if __name__ == '__main__':
    migrate_database()
