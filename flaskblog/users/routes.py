from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import LoginForm, RequestResetForm, ResetPasswordForm, UserForm, DeleteUserForm, UpdateUserForm
from flaskblog.users.utils import save_picture, send_reset_email, delete_picture

users = Blueprint('users', __name__)


@users.route("/create_user", methods=['GET', 'POST'])
def create_user():
    if current_user.get_id() != "1":
        abort(403)
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(nickname=form.nickname.data, email=form.email.data, name=form.name.data, password=hashed_password)
        if form.picture.data:
            picture_file = save_picture(form.picture.data, user.name)
            user.image_file = picture_file
        db.session.add(user)
        db.session.commit()
        flash('The account has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_user.html', title='Create a user', form=form, legend="Create a user")


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    names = User.query.with_entities(User.name)
    names = [i[0] for i in names]
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check name and password', 'danger')
    return render_template('login.html', title='Login', form=form, names=names)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route("/user/<string:nickname>", methods=["GET", "POST"])
def user_posts(nickname):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(nickname=nickname).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    form = DeleteUserForm()
    if form.validate_on_submit():
        if current_user.get_id() != "1" or user.id == 1:
            abort(403)
        for post in Post.query.filter_by(author=user):
            db.session.delete(post)
        if user.image_file != "default.jpg":
            delete_picture(user.image_file) 
        db.session.delete(user)
        db.session.commit()
        flash("User was deleted!", "success")
        return redirect(url_for("main.home"))
    return render_template('user_posts.html', posts=posts, user=user, form=form)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@users.route("/user/<string:nickname>/update", methods=["GET", "POST"])
def update_user(nickname):
    if current_user.get_id() != "1":
        abort(403)
    user = User.query.filter_by(nickname=nickname).first_or_404()
    form = UpdateUserForm()
    if form.validate_on_submit():
        user.name = form.name.data
        if form.picture.data:
            if user.image_file != "default.jpg":
                delete_picture(user.image_file)
            picture_file = save_picture(form.picture.data, user.name)
            user.image_file = picture_file
        user.nickname = form.nickname.data
        user.email = form.email.data
        db.session.commit()
        flash("User account was updated!", "success")
        return redirect(url_for("users.user_posts", nickname=user.nickname))
    elif request.method == "GET":
        form.name.data = user.name
        form.nickname.data = user.nickname
        form.email.data = user.email
    return render_template("create_user.html", title="Update " + user.nickname, form=form, legend="Update a user")

