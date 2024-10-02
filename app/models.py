from flask_login import UserMixin
from app import db


class Likes(db.Model):
    __tablename__ = "Likes"
    userID = db.Column(db.ForeignKey("User.userID"), primary_key=True)
    postID = db.Column(db.ForeignKey("Posts.postID"), primary_key=True)
    date = db.Column(db.DateTime)
    userLikes = db.relationship("User", back_populates="likes")
    postLikes = db.relationship("Posts", back_populates="likes")

class Posts(db.Model):
    __tablename__ = "Posts"
    postID = db.Column(db.String, primary_key=True)
    userID = db.Column(db.String, db.ForeignKey('User.userID'))
    title = db.Column(db.String, unique=False, nullable=True)
    content = db.Column(db.Text, unique=False, nullable=False)
    date = db.Column(db.DateTime)
    edited = db.Column(db.Boolean, default=False, nullable=False)
    likes = db.relationship("Likes", back_populates="postLikes")

class User(UserMixin, db.Model):
    __tablename__ = "User"
    userID = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    posts = db.relationship('Posts', backref='user', lazy='dynamic')
    likes = db.relationship("Likes", back_populates="userLikes")

    def get_id(self):
        return self.userID