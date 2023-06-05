from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime


# @login_required decorator ensures only signed_in users can access this page, otherwise it redirects to the login_view
# as defined in __init__.py
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get(key='page', default=1, type=int)
    # Use pagination to return SQL-Alchemy 'Pagination' object, which has an 'items' method,
    # which returns a list of items in the requested page.The number of items is defined in config.py
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)



# explore page shows all posts, not only the ones from users you are following
@app.route('/explore')
@login_required
def explore():
    page = request.args.get(key='page', default=1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


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


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get(key='page', default=1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    next_url = url_for('user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)


# flask feature to trigger function when any request is despatched to a view function by an authenticated user.
# This function triggers before the view function in question is triggered.
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    print('Form MADE')
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash("You can't follow yourself!")
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f"You are now following {username}")
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash("You can't unfollow yourself!")
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f"You have unfollowed {username}")
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))



