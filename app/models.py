from datetime import datetime
from app import db


# create user class to at to the database object
class User(db.Model):
    # create fields as database columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # create relationship by referencing to model class a 1st arg
    # this relationship is 1-many, so is created in the '1' object (in this case the user), with the 1st arg
    # representing the model class that represents the many (in this case the posts)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # __repr__ function tells python what to show when the object is printed - useful for debugging
    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # create column using field from another table using the ForeignKey,
    # calling the database table name (not the model class!) and field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'
