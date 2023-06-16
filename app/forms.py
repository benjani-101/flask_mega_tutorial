from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken, please try another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Account already exists for this email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, *kwargs)
        self.original_username = original_username
        print("args")
        print(*args)
        print("kwargs")
        print(**kwargs)

    # As a sub-class of the FlaskForm from flast-wtf, this class will automatically look for methods that begin with
    # 'validate_' followed by the name of a form field (in this case 'username') when the 'form.validate_on_submit()'
    # method is called. As such, it passes the 'username' form field as the argument, which is labeled as 'new_username'
    # within in the method context
    def validate_username(self, new_username):
        print("Username")
        print(new_username)
        if new_username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username as this one is already taken.')


# empty form for one-click actions (e.g. follow & unfollow)
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


# form for submitting blog posts
class PostForm(FlaskForm):
    post = TextAreaField("What's on your mind?", validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField()

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
