from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(name=username).first()
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')  # Optional field
        password = request.form.get('password')
        age = request.form.get('age', 18)  # Default value if age is not provided
        nationality = request.form.get('nationality', 'Unknown')

        # Check if the username already exists
        if User.query.filter_by(name=username).first():
            flash('Username already exists!', 'danger')
        else:
            try:
                new_user = User(name=username, nationality=nationality, age=age)
                new_user.password = generate_password_hash(password, method='sha256')  # Hash password
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('main.login'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {e}', 'danger')
    return render_template('register.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
