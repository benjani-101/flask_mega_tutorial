from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Ben'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # form.validate_on_submit() returns False if browser sends 'GET' request to receive the web page containing the form
    # and returns False if the browser sends the 'POST' request as a result of the user pressing the submit button and
    # all the validators attached to the fields are passed. If any validators fail, it returns False.
    if form.validate_on_submit():
        flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
