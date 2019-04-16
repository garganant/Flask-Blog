import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        pw_hash=bcrypt.generate_password_hash(user.password).decode('utf-8')
        if user and bcrypt.check_password_hash(pw_hash,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.splitext(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static/profile_pics',picture_fn)

    output_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

    @app.route("/account")
    @login_required
    def account():
        form=UpdateAccountForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file=save_picture(form.picture.data)
                current_user.image=picture_file
            current_user.username=form.username.data
            current_user.email=form.email.data
            db.session.commit()
            flash('Your account has been updated','success')
            return redirect(url_for('account'))
        elif request.method=="GET":
            form.username.data=current_user.username
            form.email.data=current_user.email
        image_file=url_for('static', filename='profile_pics/'+ current_user.image_file)
        return render_template('Account.html', title="Account", image_file=image_file, form=form)
