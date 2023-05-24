from flask import render_template
from app import app


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