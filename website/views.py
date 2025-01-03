from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Crime, User, Category, Location, Chat
from . import db
from datetime import datetime
from collections import defaultdict
from collections import Counter
from flask import redirect, url_for
import json
from datetime import datetime
from flask import session
from flask import render_template, request, flash
from geopy.geocoders import Nominatim
import folium
import requests
import folium
from geopy.geocoders import Nominatim
from folium.plugins import MarkerCluster
from .models import Crime, User

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        text = request.form['text']

        # Add the new chat message to the database
        new_message = Chat(user_id=current_user.id, text=text)
        db.session.add(new_message)
        db.session.commit()

        return redirect(url_for('views.home'))

    # Fetch all chat messages
    chats = Chat.query.all()
    crimes = Crime.query.all()
    categories = Category.query.all()
    for crime in crimes:
        crime.user = User.query.get(crime.user_id)
    return render_template("home.html", user=current_user, crimes=crimes, categories=categories, chats=chats)

@views.route('/clear_chats', methods=['POST'])
def clear_chats():
    if current_user.id == 1:  # Ensure the user is the admin (or any role you prefer)
        Chat.query.delete()  # This deletes all records in the Chat table
        db.session.commit()  # Commit the changes to the database
    return redirect(url_for('views.home'))  # Redirect back to the home page


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
 
        if 'add-category' in request.form:
            name = request.form.get('category-name')
            if Category.query.filter_by(name=name).first():
                flash('Category already exists.', category='error')
            else:
                new_category = Category(name=name)
                db.session.add(new_category)
                db.session.commit()
                flash('Category added successfully!', category='success')

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

@views.route('/stats', methods=['GET'])
@login_required
def stats():
    # Fetch all crimes
    crimes = Crime.query.all()
    location_filter = request.args.get('location', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        start_date = datetime.min  
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        end_date = datetime.max 

    filtered_crimes = [
        crime for crime in crimes
        if (start_date <= crime.date <= end_date) and (location_filter == '' or crime.location == location_filter)
    ]

    location_counts = Counter([crime.location for crime in crimes])
    locations = list(location_counts.keys())
    counts = list(location_counts.values())

    return render_template('stats.html',
        user=current_user,
        locations=locations,
        counts=counts,
        location_filter=location_filter,
        crime_count=len(filtered_crimes),location_counts=location_counts, crimes=crimes)
    
@views.route('/delete-crime/<int:crime_id>', methods=['POST'])
@login_required
def delete_crime(crime_id):
    if current_user.id != 1:  # Restrict access to admin
        flash('Access denied!', category='error')
        return redirect(url_for('views.home'))

    crime = Crime.query.get(crime_id)
    if crime:
        db.session.delete(crime)
        db.session.commit()
        flash('Crime deleted successfully!', category='success')
    else:
        flash('Crime not found.', category='error')
    return redirect(url_for('views.admin_tools'))  # Redirect back to admin tools page

#----------------------------------------------------------------------------------------------


@views.route('/submit_crime', methods=['POST'])
def submit_crime():
    title = request.form.get('title')
    description = request.form.get('description')
    location = request.form.get('location')
    date = request.form.get('date')
    

    if title and description and location and date:
        new_crime = Crime(title=title, description=description, location=location, date=date, user_id=current_user.id)
        db.session.add(new_crime)
        db.session.commit()
        return redirect(url_for('views.law_enforcement'))
    else:
        return redirect(url_for('views.law_enforcement', error='Please fill in all fields'))

@views.route('/report_crime', methods=['GET', 'POST'])
@login_required
def report_crime():
    crimes = Crime.query.all()
    categories = Category.query.all()
    if request.method == 'POST': 
        title = request.form.get('Title')  
        location = request.form.get('Location')  
        data = request.form.get('Description')  
        category_id = request.form.get('category-id')  

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
                user_id=current_user.id )
            db.session.add(new_Crime)

            selected_category = Category.query.filter_by(cat_id=category_id).first()
            if selected_category:
                selected_category.count += 1
                db.session.commit()
                flash('Crime posted and category updated!', category='success')
            else:
                flash('Invalid category selected!', category='error')
    return render_template("report_crime.html", user=current_user, crimes=crimes, categories=categories)

@views.route('/law_enforcement', methods=['GET', 'POST'])
@login_required
def law_enforcement():
    if current_user.id != 1: 
        flash('Access denied!', category='error')
        return redirect(url_for('views.home'))

    crimes = Crime.query.all()  
    for crime in crimes:
        crime.user = User.query.get(crime.user_id)
    return render_template('law_enforcement.html', user=current_user, crimes=crimes)


@views.route('/community_resources', methods=['GET'])
@login_required
def community_resources():
    return render_template('community_resources.html', user=current_user)


@views.route('/public_awareness', methods=['GET'])
@login_required
def public_awareness():
    return render_template('public_awareness.html', user=current_user)


@views.route('/educational_resources', methods=['GET'])
@login_required
def educational_resources():
    return render_template('educational_resources.html', user=current_user)

@views.route('/live-map', methods=['GET', 'POST'])
@login_required



def live_map():
    # BRAC University coordinates (fallback location)
    brac_location = [23.7725, 90.4253]  # Coordinates for BRAC University
    zoom_level = 16

    # Create the folium map centered at BRAC University by default
    m = folium.Map(location=brac_location, zoom_start=zoom_level, tiles='cartodbdark_matter')

    # Add the blue marker and circle for BRAC University
    folium.CircleMarker(
        location=brac_location,
        radius=10,
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=0.6,
        popup="BRAC University"
    ).add_to(m)
    folium.Marker(brac_location, popup="BRAC University").add_to(m)

    if request.method == 'POST':
        if 'center_on_user' in request.form:
            # Get user location from JavaScript (sent via POST request)
            user_lat = request.form.get('latitude')
            user_lng = request.form.get('longitude')

            # If the user location is provided, center the map on it
            if user_lat and user_lng:
                user_location = [float(user_lat), float(user_lng)]
                m = folium.Map(location=user_location, zoom_start=zoom_level, tiles='cartodbdark_matter')

                # Add the blue marker and circle for the user's location
                folium.CircleMarker(
                    location=user_location,
                    radius=10,
                    color="blue",
                    fill=True,
                    fill_color="blue",
                    fill_opacity=0.6,
                    popup="Your Location"
                ).add_to(m)
                folium.Marker(user_location, popup="Your Location").add_to(m)
            else:
                # If geolocation failed or no user location is available, center map on BRAC University
                m = folium.Map(location=brac_location, zoom_start=zoom_level, tiles='cartodbdark_matter')
                folium.CircleMarker(
                    location=brac_location,
                    radius=10,
                    color="blue",
                    fill=True,
                    fill_color="blue",
                    fill_opacity=0.6,
                    popup="BRAC University"
                ).add_to(m)
                folium.Marker(brac_location, popup="BRAC University").add_to(m)

    # Render the map as HTML to be injected into the template
    map_html = m._repr_html_()
    return render_template('live_map.html', map_html=map_html, user=current_user)


# Function to get the user location based on their IP
def get_user_location():
    try:
        # You can use the IPInfo API to get the user's location based on their IP address
        ip_info = requests.get('https://ipinfo.io/json').json()
        loc = ip_info['loc'].split(',')  # loc returns a string like "lat,long"
        lat = float(loc[0])
        lon = float(loc[1])
        return [lat, lon]
    except Exception as e:
        print("Error in getting user location:", e)
        return [23.8103, 90.4125]  # Default to Dhaka if location cannot be fetched

