from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


# create user class to at to the database object
# Inherit UserMixin class from flask_login to get the four attributes required to work with flask_login:
# 3 Booleans - is_authenticated; is_active, is_anonymous;
# 1 str - get_id() (this returns a unique id for the user)
class User(UserMixin, db.Model):
    # create fields as database columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # create relationship by referencing to model class a 1st arg
    # this relationship is 1-many, so is created in the '1' object (in this case the user), with the 1st arg
    # representing the model class that represents the many (in this case the posts)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # Additional info
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # __repr__ function tells python what to show when the object is printed - useful for debugging
    def __repr__(self):
        return f'<User {self.username}>'

    # function for setting password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # function for checking password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # return avatar from 'Gravatar'
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'





class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # create column using field from another table using the ForeignKey,
    # calling the database table name (not the model class!) and field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))