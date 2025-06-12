from flask import Blueprint,render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required, current_user, logout_user

from .forms import RegisterForm, LoginForm
from app.extensions import db,login_manager

from .models import User

main = Blueprint('main',__name__)




@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register',methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data,email=form.email.data,password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created succesfully')
        return redirect(url_for('main.login'))
    return render_template('register.html',form=form)

@main.route('/login',methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password,form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('invalid credentials')
    return render_template('login.html',form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    return f'Welcome {current_user.username}! This is yoyr dash board'

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))
            

        
