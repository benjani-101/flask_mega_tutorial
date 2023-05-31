from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


# @login_required decorator ensures only signed_in users can access this page, otherwise it redirects to the login_view
# as defined in __init__.py
@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Chorley'
        },
        {
            'author': {'username': 'Christine'},
            'body': 'Great weather for a dog walk!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if user is already logged in, go straight to home page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    # form.validate_on_submit() returns False if browser sends 'GET' request to receive the web page containing the form
    # and returns False if the browser sends the 'POST' request as a result of the user pressing the submit button and
    # all the validators attached to the fields are passed. If any validators fail, it returns False.
    if form.validate_on_submit():
        # get username from user table in database by filtering using value given in the form
        user = User.query.filter_by(username=form.username.data).first()
        # check the user exists in the database and the password is correct
        if user is None or not user.check_password((form.password.data)):
            flash('Invalid username or password given')
            return redirect(url_for('login'))
        login_user(user=user, remember=form.remember_me.data)
        # next page will get the original page the user attempted to access before logging in
        # (next query string added by @login_required decorator). If the page was accessed directly,
        # logging in will result in a redirect to the homepage
        next_page = request.args.get('next')
        # the second condition checks if the url is relative or absolute (i.e. including domain name).
        # Oonly redirects to 'next_page' if url is relative to prevent bad actors inserting other domains to redirect to
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered, welcome to the blog!')
        return redirect(url_for('login'))
    print(form.errors)
    return render_template('register.html', title='Register', form=form)

