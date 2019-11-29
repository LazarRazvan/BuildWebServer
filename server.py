import os
import sys
import hashlib
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
from influxdb import InfluxDBClient

"""
>>> client.write(['users,hashid=%s name=%s,pass=%s' % ("1231", "21", "521")], {'db':'users'}, protocol='line')
True
>>> 
>>> 
>>> client.query('SELECT * FROM "users"', database="users")
ResultSet({'('users', None)': [{'time': '2019-11-18T21:00:39.361545913Z', 'hashid': '1231', 'name': 21, 'pass': 521}]})
"""

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
CLIENT = None
DB_NAME = "users"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if False:
    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('uploaded_file',
                                        filename=filename))
        return render_template("index.html")



@app.route('/', methods=['GET', 'POST'])
def welcome():
    """
    This function is used to render welcome page. We don't accept
    POST/GET methods here because we use redirect.
    """
    return render_template("index.html");

#LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This function will be called when user wants to login
    """
    error = None
    print ("login function is called")
    if request.method == 'POST':
        user = request.form.get('username')
        pswd = request.form.get('password')
        # Create user hash by username and password
        user_hash = create_hash(user, pswd).hexdigest()

        if "email" in request.form:
            # Sign In : Add data to InfluxDB
            email = request.form.get('email')
            err = CLIENT.write(['%s,hashid=%s name=%s,pass=%s,email=%s' % (DB_NAME, user_hash, user, pswd, email)], {'db':DB_NAME}, protocol='line')
            if err:
                print ("Fail to add user = %s" % (user))
        else:
            # Log In : Query InfluxDB to find hash
            results = CLIENT.query('SELECT "name" FROM "%s"' % (DB_NAME))
            print ("DB : %s" % (results.raw))

        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/build?')

    return render_template('login.html', error=error)

#ABOUT
@app.route('/about', methods=['GET', 'POST'])
def about():
    """
    This function is called when about page is opened.
    """
    print ("About function is called")
    return render_template("about.html")

@app.route('/build', methods=['GET', 'POST'])
def build():
    """
    This function is called after login. It allow users to upload
    files to be compiled and update statistics.
    """
    if request.method == 'POST':
        print ("request_form = " + request.form)
    return render_template("build.html");

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def start_database(host_name, port_nr, db_name):
    """
    Start InfluxDB where authentification data will be stored
    host_name:  hostname where InfluxDB will run
    port_nr :   port used by InfluxDB
    db_name :   database name to store users
    """
    global CLIENT
    CLIENT = InfluxDBClient(host=host_name, port=port_nr)

    if not CLIENT:
        sys.exit("Fail to start InfluxDB on host %s and port %d" % (host_name, port_nr))

    # Check if database is created. If not, create it
    databases_dict = CLIENT.get_list_database()
    print ("Databases : %s" % (databases_dict))
    databases = [d['name'] for d in databases_dict if 'name' in d]
    if db_name not in databases:
        CLIENT.create_database(db_name)
        CLIENT.switch_database(db_name)
    else:
        # Database already exists. Do you want to delete?
        CLIENT.switch_database(db_name)
        results = CLIENT.query('SELECT "name" FROM "%s"' % (DB_NAME))
        print ("Current recordings : %s" % (results.raw))
        key = input("Do you want to delete current database[y/n]?")
        if key == 'y':
            print("Deleting %s database ..." % (DB_NAME))
            CLIENT.drop_database(DB_NAME)
            CLIENT.create_database(db_name)
            CLIENT.switch_database(db_name)

def create_hash(username, password):
    """
    Create a hash to be used by server to identify a user
    username    : User name
    password    : User password
    """
    string = ('%s%s' % (username, password)).encode('utf-8')
    hash = hashlib.md5()
    hash.update(string)
    return hash

if __name__ == "__main__":
    start_database('localhost', 8086, DB_NAME)
    app.run(host="0.0.0.0")