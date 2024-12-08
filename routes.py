from flask import render_template, request, redirect, url_for, flash
from app import app, mysql, bcrypt
from werkzeug.utils import secure_filename
import os
from flask import jsonify
from flask import session

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        role = 'public'
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                       (username, email, password, role))
        mysql.connection.commit()
        cursor.close()
        flash("Registration Successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and bcrypt.check_password_hash(user[3], password):
            flash("Login Successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, please try again.", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return "Welcome to the CrimeMap Dashboard"


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/report-crime', methods=['GET', 'POST'])
def report_crime():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_time = request.form['date_time']
        location = request.form['location']
        crime_type = request.form['crime_type']
        media_file = request.files['media_file']

        filename = None
        if media_file and allowed_file(media_file.filename):
            filename = secure_filename(media_file.filename)
            media_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO crimes (title, description, date_time, location, crime_type, media_file, reported_by) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (title, description, date_time, location, crime_type, filename, 1))  # Use session['user_id'] later
        mysql.connection.commit()
        cursor.close()

        flash("Crime reported successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('report_crime.html')




@app.route('/map')
def map_view():
    return render_template('map.html')

@app.route('/api/crimes')
def get_crimes():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT title, description, date_time, crime_type, latitude, longitude FROM crimes")
    crimes = cursor.fetchall()
    cursor.close()

    crime_list = [
        {
            "title": crime[0],
            "description": crime[1],
            "date_time": str(crime[2]),
            "crime_type": crime[3],
            "latitude": crime[4],
            "longitude": crime[5]
        } for crime in crimes
    ]
    return jsonify(crime_list)




@app.route('/report_crime', methods=['GET', 'POST'])
def report_crime():
    if 'user_id' not in session:
        flash("Please log in to report a crime.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        crime_type = request.form['crime_type']
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO crime_reports (user_id, title, description, location, crime_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, title, description, location, crime_type))
        mysql.connection.commit()
        cursor.close()

        flash("Crime report submitted successfully!", "success")
        return redirect(url_for('dashboard'))
    
    return render_template('report_crime.html')