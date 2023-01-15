# Importing flask module
from flask import Flask, template_rendered
from flask import render_template, request, redirect, url_for, flash, session
from flask import send_from_directory
from flask_session import Session
from werkzeug.utils import secure_filename
import sqlite3
import os
import cv2
import glob
import sys
import binascii
import argparse

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# App creation
app = Flask("Flask - Lab")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_EXTS'] = [".png", ".jpg", ".jpeg", ".gif", ".tiff"]
# Session creation
sess = Session()

# SqlLite db file path
DATABASE = 'database.db'

@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    # Db connection
    conn = sqlite3.connect(DATABASE)
    # Create tables with sqlite3
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, isAdmin TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS scores (id int NOT NULL AUTO_INCREMENT, player TEXT, score TEXT)')
    # Terminate the db connection
    conn.close()
    
    return index()

@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    # Db connection
    conn = sqlite3.connect(DATABASE)
    # Create tables with sqlite3
    conn.execute('INSERT INTO users VALUES ("admin", "admin", "yes")')
    # Terminate the db connection
    conn.close()
    
    return index()


@app.route('/score.html', methods=['GET', 'POST'])
def index():

    if 'user' in session:
        con = sqlite3.connect(DATABASE)
    
        # Fetch data from table
        cur = con.cursor()
        cur.execute("select * from scores")
        scores = cur.fetchall();  

        return render_template('score.html', scores = scores)

    else:
        return render_template('login.html')
    
@app.route('/Website.html', methods=['GET', 'POST'])
def main():

    if 'user' in session:
        con = sqlite3.connect(DATABASE)
    
        # Fetch data from table
        #cur = con.cursor()
        #cur.execute("select * from scores")
        #scores = cur.fetchall();  

        #return render_template('Website.html', scores = scores)
        return render_template('Website.html')

    else:
        return render_template('login.html')
    
@app.route('/', methods=['GET', 'POST'])
def home():

    if 'user' in session:
        con = sqlite3.connect(DATABASE)
        return render_template('Website.html')

    else:
        return render_template('login.html') 
    
@app.route('/Site2.html', methods=['GET', 'POST'])
def pictures():

    if 'user' in session:
        con = sqlite3.connect(DATABASE)
        return render_template('Site2.html')

    else:
        return render_template('login.html')
 
@app.route('/Site2upload.html', methods=['GET', 'POST'])
def picturesup():

    if 'user' in session:
        con = sqlite3.connect(DATABASE)
        return render_template('Site2upload.html')

    else:
        return render_template('login.html')
   
@app.route('/Site2upload', methods=['GET', 'POST'])
def picturesupload():

    if request.method == 'POST':
        # Upload file flask
        uploaded_img = request.files['uploaded-file']
        # Extracting uploaded data file name
        img_filename = secure_filename(uploaded_img.filename)
        # Upload file to database (defined uploaded folder in static path)
        uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
        # Storing uploaded file path in flask session
        session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
 
        return render_template('Site2upload2.html')


@app.route('/Site2show')
def displayImage():
    # Retrieving uploaded file path from session
    img_file_path = session.get('uploaded_img_file_path', None)
    # Display image in Flask application web page
    return render_template('Site2show.html', user_image = img_file_path)

@app.route('/Site2gal')
def displayGall():
    pics = os.listdir('static/uploads')
    pics = ['uploads/' + file for file in pics]
    return render_template('Site2show2.html', pics = pics)

@app.route('/Site3.html', methods=['GET', 'POST'])
def game():

    if 'user' in session:
        con = sqlite3.connect(DATABASE)
        
        username = session["user"]
        print("Hello World")
        return render_template('Site3.html', username = username) 

    else:
        return render_template('login.html')
    
@app.route('/Site4.html', methods=['GET', 'POST'])
def adminpanel():
    if 'user' in session:
        currentLoggedUser = session["user"]
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("select * from users where username=?", (currentLoggedUser, ))
        currentUser = cur.fetchone()
        if currentUser[2] != 'yes':
            return f'Insufficient priviliges' + home()
        else:
            cur2 = con.cursor()
            cur2.execute("select * from users")
            users = cur2.fetchall()
            con.close()
            username = session["user"]
            return render_template('Site4.html', username = username, users = users) 
    else:
        return render_template('login.html') 

@app.route('/add_user', methods=['POST'])
def addUser():
        username = request.form['username']
        password = request.form['password']
        isAdmin = 'no' if (request.form.get('isAdmin') is None) else 'yes'        
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("INSERT INTO users (username,password,isAdmin) VALUES (?,?,?)",(username,password,isAdmin))
        con.commit()
        cur.execute("select * from users")
        users = cur.fetchall(); 
        username = session["user"]
        con.close()

        return "User succesfully added <br>" + render_template('Site4.html', username = username, users = users) 
       
@app.route('/authenticate', methods=['POST'])
def authenticate():

    username = request.form['username']
    password = request.form['password']
    #adstatus = request.form['isAdmin']
    print(username)
    print(password)
    print()
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("select * from users where username=?", (username, ))
    requestedUser = cur.fetchone()
    con.close()
    print(requestedUser)
    if requestedUser is None or requestedUser[1] != password:
        return "Invalid username or password"

    session["user"] = username
    
    return f'Hello, welcome {username}' + home()    
    
@app.route('/logout.html', methods=['GET'])
def logOut():
    # If the user session exists - remove it
    if 'user' in session:
        session.pop('user')
     
    else:
        # Redirect the client to the homepage
        redirect(url_for('index'))
    
    return render_template('logout.html')

@app.route('/login.html', methods=['GET', 'POST'])
def logIn():
    # If the user session exists - remove it
    if 'user' in session:
        session.pop('user')
     
    else:
        # Redirect the client to the homepage
        redirect(url_for('index'))
    
    return render_template('logout.html')    
    # Start the app in debug mode
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.run(debug = True)

