import os
import sys
import hashlib
import datetime
from flask import Flask, flash, request, redirect, url_for, render_template
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.utils import secure_filename
from flask import send_from_directory
from influxdb import InfluxDBClient

UPLOAD_FOLDER = None
ALLOWED_EXTENSIONS = set(['zip', 'rar', 'tar'])
CLIENT = None
DB_NAME = "users"
LOG_FILE = '/var/log/webserver'


app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('webserver_info', 'Application info', version='1.0.3')

# Ensure that only allowed files will be uploaded
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def welcome():
    """
    This function is used to render welcome page. We don't accept
    POST/GET methods here because we use redirect.
    """
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This function will be called when user wants to login
    """
    error = None
    if request.method == 'POST':
        user = request.form.get('username')
        pswd = request.form.get('password')
        # Create user hash by username and password
        user_hash = create_hash(user, pswd).hexdigest()

        if "email" in request.form:
            # Sign In : Add data to InfluxDB
            email = request.form.get('email')
            err = CLIENT.write(['%s,hashid=%s name="%s",pass="%s",email="%s"' % (DB_NAME, user_hash, user, pswd, email)], {'db':DB_NAME}, protocol='line')
            if not err:
                flash ("Fail to Sing in user")
        else:
            # Log In : Query InfluxDB to find hash
            results = list(CLIENT.query('SELECT * FROM "%s" WHERE "hashid" = \'%s\'' % (DB_NAME, user_hash)))
            if results:
                # We have an entry for this user
                return redirect('/build?hash=%s' % (user_hash))
            else:
                flash("Fail to login")

    return render_template('login.html', error=error)

@app.route('/about', methods=['GET', 'POST'])
def about():
    """
    This function is called when about page is opened.
    """
    return render_template("about.html")

@app.route('/build', methods=['GET', 'POST'])
def build():
    """
    This function is called after login. It allow users to upload
    files to be compiled and update statistics.
    """
    hashid = request.args.get('hash', default = '', type = str)

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
            # Rename the archive with the user hashid to be identified in grafana
            log_to_file("Previous name = %s" % file.filename)
            file.filename = "%s.zip" % hashid
            log_to_file("Name after change name = %s" % file.filename)
            filename = secure_filename(file.filename)
            err = file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            log_to_file("Save %s file to %s, err = %s" % (UPLOAD_FOLDER, filename, err))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
        else:
            flash ("File extension not allowed")
    return render_template("build.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def log_to_file(message):
    """
    Add a message to log file

    @message: Line to be logged
    """
    with open(LOG_FILE, "a") as log:
        log.write("[%s]: %s\n" % (datetime.datetime.now(), message))

def start_database(host_name, port_nr, db_name):
    """
    Start InfluxDB where authentification data will be stored
    host_name:  hostname where InfluxDB will run
    port_nr :   port used by InfluxDB
    db_name :   database name to store users
    """
    global CLIENT
    global UPLOAD_FOLDER

    UPLOAD_FOLDER = sys.argv[2]
    CLIENT = InfluxDBClient(host=host_name, port=port_nr)

    if not CLIENT or not UPLOAD_FOLDER:
        log_to_file("Fail to start InfluxDB on host %s and port %d" % (host_name, port_nr))
        sys.exit(-1)

    # Check if database is created. If not, create it
    databases_dict = CLIENT.get_list_database()
    log_to_file("Databases : %s" % (databases_dict))
    databases = [d['name'] for d in databases_dict if 'name' in d]
    if db_name not in databases:
        log_to_file("Creating database : %s ..." % db_name)
        CLIENT.create_database(db_name)
        CLIENT.switch_database(db_name)
    else:
        # Database already exists. Do you want to delete?
        CLIENT.switch_database(db_name)
        results = CLIENT.query('SELECT "name" FROM "%s"' % (DB_NAME))
        log_to_file("Results in database : %s" % (results.raw))
        #key = input("Do you want to delete current database[y/n]?")
        key = 'y'
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
    # InfluxDB hostname should be sent as first param
    if len(sys.argv) - 1 != 2:
        sys.exit(-1)

    DB_HOSTNAME = sys.argv[1]

    start_database(DB_HOSTNAME, 8086, DB_NAME)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.run(host="0.0.0.0")
