from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt
from app.models import Client, Admin
from flask_login import login_user, current_user, logout_user, login_required

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    errors = {}

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')

        if not name:
            errors['name'] = 'Name is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not password:
            errors['password'] = 'Password is required.'
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'
        if not phone:
            errors['phone'] = 'Phone is required.'

        existing_client = Client.query.filter_by(email=email).first()
        if existing_client:
            errors['email'] = 'That email is already taken. Please choose a different one.'
        if not errors:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            client = Client(name=name, email=email, password=hashed_password, phone=phone)
            db.session.add(client)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', errors=errors)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    errors = {}

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        if not email:
            errors['email'] = 'Email is required.'
        if not password:
            errors['password'] = 'Password is required.'
        if not user_type:
            errors['user_type'] = 'User type is required.'

        user = None
        if user_type == 'client':
            user = Client.query.filter_by(email=email).first()
        elif user_type == 'admin':
            user = Admin.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user_type == 'client':
                return redirect(url_for('main.home'))
            elif user_type == 'admin':
                return redirect(url_for('main.admin_dashboard'))
        else:
            errors['login'] = 'Login Unsuccessful. Please check email, password, and user type.'

    return render_template('auth/login.html', title='Login', errors=errors)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
