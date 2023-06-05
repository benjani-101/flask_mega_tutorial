from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

# create 'followers' association table containing follower_id and followed_id columns
# (new class not needed as it is an auxiliary table that only consists of foreign keys from existing classes)
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


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

    # list of people followed created by relationship links between User Instances, which is why first arg is 'User'
    # many-many relationship with followers table. The backref is used to show how the relationship is accessed from
    # the other side (i.e. by the followed user) which is represented by the new field 'followers' in the user table
    # The additional lazy argument indicates the execution mode for this query.
    # A mode of dynamic sets up the query to not run until specifically requested
    # Setting up in this way allows this followed field to behave like a list due to SQLAlchemy ORM
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

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

    # method for following other user
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    # method for unfollowing other user
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    # method for checking user is following other user
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    # method for displaying most recent posts from followed users
    def followed_posts(self):
        followed_posts = Post.query.join(  # used to join Posts table to followers table
                                           # where followed_id matches post's user_id
            followers, (followers.c.followed_id == Post.user_id)).filter(  # filtered so follower_id is user_id
            followers.c.follower_id == self.id)

        own_posts = Post.query.filter_by(  # filtered so post's user_id is user_id
            user_id=self.id)

        # return combination of own and followed posts sorted by timestamp field in Post
        return followed_posts.union(own_posts).order_by(Post.timestamp.desc())


# class for 'post' objects that inherits from db.Model, creating a table in db representing all posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # create column using field from another table using the ForeignKey,
    # calling the database table name (not the model class!) and field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'


# function that allows the app access to the user based on the id throughout the session
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


