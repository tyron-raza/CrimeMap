from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Crime, User
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        title = request.form.get('Title')  # Gets the title from the HTML form
        location = request.form.get('Location')  # Gets the location from the HTML form
        data = request.form.get('Description')  # Gets the crime description from the HTML form

        # Validation
        if not title or len(title) < 3:
            flash('Title is too short!', category='error')
        elif not location or len(location) < 3:
            flash('Location is too short!', category='error')
        elif not data or len(data) < 5:
            flash('Description is too short!', category='error')
        else:
            # Create and save a new crime report
            new_Crime = Crime(
                title=title,
                location=location,
                data=data,
                user_id=current_user.id
            )
            db.session.add(new_Crime)
            db.session.commit()
            flash('Crime posted!', category='success')

    # Fetch all crimes to display on the page
    crimes = Crime.query.all()
    for crime in crimes:
        # Query the associated user using the user_id foreign key
        crime.user = User.query.get(crime.user_id)
    return render_template("home.html", user=current_user, crimes=crimes)


@views.route('/delete-Crime', methods=['POST'])
def delete_Crime():  
    Crime = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    CrimeId = Crime['CrimeId']
    Crime = Crime.query.get(CrimeId)

    return jsonify({})
