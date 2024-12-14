from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Crime, User, Category
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        title = request.form.get('Title')  
        location = request.form.get('Location')  
        data = request.form.get('Description')  

        if not title or len(title) < 3:
            flash('Title is too short!', category='error')
        elif not location or len(location) < 3:
            flash('Location is too short!', category='error')
        elif not data or len(data) < 5:
            flash('Description is too short!', category='error')
        else:
            new_Crime = Crime(
                title=title,
                location=location,
                data=data,
                user_id=current_user.id
            )
            db.session.add(new_Crime)
            db.session.commit()
            flash('Crime posted!', category='success')

    crimes = Crime.query.all()
    for crime in crimes:
        crime.user = User.query.get(crime.user_id)
    return render_template("home.html", user=current_user, crimes=crimes)

@views.route('/admin-tools', methods=['GET', 'POST'])
@login_required
def admin_tools():
    if current_user.id != 1:
        flash('Access denied!', category='error')
        return redirect(url_for('views.home'))

    crimes = Crime.query.all()
    for crime in crimes:
        crime.user = User.query.get(crime.user_id)
    categories = Category.query.all()

    if request.method == 'POST':
        # Add new category
        if 'add-category' in request.form:
            name = request.form.get('category-name')
            if Category.query.filter_by(name=name).first():
                flash('Category already exists.', category='error')
            else:
                new_category = Category(name=name)
                db.session.add(new_category)
                db.session.commit()
                flash('Category added successfully!', category='success')
        # Remove category
        elif 'remove-category' in request.form:
            cat_id = request.form.get('category-id')
            category = Category.query.get(cat_id)
            if category:
                db.session.delete(category)
                db.session.commit()
                flash('Category removed successfully!', category='success')
            else:
                flash('Category not found.', category='error')

    return render_template('admin_tools.html',user=current_user, crimes=crimes, categories=categories)

@views.route('/delete-crime/<int:crime_id>', methods=['POST'])
@login_required
def delete_crime(crime_id):
    if current_user.id != 1:
        flash('Access denied!', category='error')
        return redirect(url_for('views.home'))
    crime = Crime.query.get(crime_id)
    if crime:
        db.session.delete(crime)
        db.session.commit()
        flash('Crime deleted successfully!', category='success')
    else:
        flash('Crime not found.', category='error')
    return redirect(url_for('views.admin_tools'))
