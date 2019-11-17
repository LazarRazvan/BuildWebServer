import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This function will be called when user wants to login
    """
    error = None
    print ("login function is called")
    if request.method == 'POST':
        print ("Method is post %s %s" %(request.form['username'], request.form['password']))
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/build?')

    return render_template('login.html', error=error)

@app.route('/build', methods=['GET', 'POST'])
def build():
    """
    This function is called after login. It allow users to upload
    files to be compiled and update statistics.
    """
    if request.method == 'POST':
        print ("request_form = " + request.form)
    return render_template("build.html");

@app.route('/about', methods=['GET', 'POST'])
def about():
    """
    This function is called when about page is opened.
    """
    print ("About function is called")
    return render_template("about.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
