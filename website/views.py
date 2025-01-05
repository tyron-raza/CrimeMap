from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Crime, User, Category, Chat
from . import db
from datetime import datetime
from collections import defaultdict
from collections import Counter
from datetime import datetime
import requests
import folium
from geopy.geocoders import Nominatim
import random

views = Blueprint('views', __name__)




response= None
brac_location = [23.7725, 90.4253]
default_location= brac_location  
zoom_level = 14
searched_location = None 
m = folium.Map(location=default_location, zoom_start=zoom_level, tiles='cartodbdark_matter')
crime_locations= []

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    clear_markers()
    global crime_locations, m
    m = folium.Map(location=default_location, zoom_start=zoom_level, tiles='cartodbdark_matter')
    if request.method == 'POST':
        text = request.form['text']

        new_message = Chat(user_id=current_user.id, text=text)
        db.session.add(new_message)
        db.session.commit()

        return redirect(url_for('views.home'))
   
    chats = Chat.query.all()
    crimes = Crime.query.all()
    categories = Category.query.all()
    for crime in crimes:
        crime.user = User.query.get(crime.user_id)
        if crime.location not in crime_locations:
            crime_locations.append(crime.location)
    for crime_location in crime_locations:
        if crime_location:  
           geolocator = Nominatim(user_agent="crime_map")
           location = geolocator.geocode(crime_location)  
           if location:
               searched_location = [location.latitude, location.longitude]     
               folium.CircleMarker(
                   location=searched_location,
                   radius=random.randint(10,50),
                   color="red",
                   fill=True,
                   fill_color="red",
                   fill_opacity=0.2,
                   popup= f'{crime_location}'
               ).add_to(m)

    return render_template("home.html", user=current_user, crimes=crimes, categories=categories, chats=chats)

@views.route('/clear_chats', methods=['POST'])
def clear_chats():
    if current_user.id == 1:  
        Chat.query.delete() 
        db.session.commit() 
    return redirect(url_for('views.home')) 


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

#----------------------------------------------------------------------------------------------

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

@views.route('/live-map', methods=['GET', 'POST', "center_on_user"])
@login_required
def live_map():
    global response, brac_location,default_location,zoom_level,searched_location,m
    response= None
    m.location= brac_location
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
    if request.method == 'POST':
        search_query = request.form.get('location')

        if search_query:
            geolocator = Nominatim(user_agent="crime_map")
            location = geolocator.geocode(search_query) 
            if location:
                searched_location = [location.latitude, location.longitude]
        
                folium.Marker(
                    [location.latitude, location.longitude],
                    popup= location.address,
                    tooltip="Searched Location",
                    icon=folium.Icon(color="red")
                ).add_to(m)
            m.location = searched_location
            
    elif request.method =='center_on_user':
        clear_markers()
        response = requests.get("https://ipinfo.io/json")
        if response and response.status_code == 200:
            data = response.json()
            location = data.get("loc", "")           
            # If the user location is provided, center the map on it
            if location:
                latitude, longitude = map(float, location.split(","))
                user_location= [float(latitude), float(longitude)]
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
                folium.Marker(user_location, popup="Your Location", icon=folium.Icon(color="red")).add_to(m)
                m.location = user_location
            else:
                # If geolocation failed or no user location is available, center map on BRAC University
                folium.CircleMarker(
                    location=brac_location,
                    radius=10,
                    color="blue",
                    fill=True,
                    fill_color="blue",
                    fill_opacity=0.6,
                    popup="BRAC University"
                ).add_to(m)
                folium.Marker(brac_location, popup="BRAC University", icon=folium.Icon(color="red")).add_to(m)
                m.location = brac_location
 
    map_html = m._repr_html_()
    return render_template('live_map.html', map_html=map_html, user=current_user)

def clear_markers():
    brac_location = [23.7725, 90.4253]
    default_location= brac_location  # Coordinates for BRAC University
    zoom_level = 16
    m = folium.Map(location=default_location, zoom_start=zoom_level, tiles='cartodbdark_matter')

