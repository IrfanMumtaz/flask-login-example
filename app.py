from flask import Flask, render_template, session, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from flask_pymongo import PyMongo
from bson.json_util import dumps
from flask_bcrypt import Bcrypt

import time

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'loginpanel'
app.config['MONGO_URI'] = 'mongodb://loginpanel:loginpanel*123*@ds115396.mlab.com:15396/loginpanel'
app.config['SECRET_KEY'] = 'qGE2JkgBwMIl79erSglvGe3oOnrvxSYl'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)



class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    user = User()
    user.id = email
    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        result = users.find_one({'email': request.form['email']})
        if result is None:

            form = {
                'name': request.form['name'],
                'email': request.form['email'],
                'password': bcrypt.generate_password_hash(request.form['password']),
                'created_at': time.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': time.strftime('%d-%m-%Y %H:%M:%S')
            }   

            users.insert(form)
            user = User()
            user.id = request.form['email']
            return redirect(url_for('index'))
        
        return '<h2>This user is already exist, please try another</h2>'
    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        result = users.find_one({'email': request.form['email']})
        if result is None:
            return '<h2>Invalid credentials</h2>'
        
        elif bcrypt.check_password_hash(result['password'], request.form['password']):
            user = User()
            user.id = result['email']
            login_user(user)
            return redirect(url_for('index'))

        else:
            return '<h2>Invalid credentials</h2>'

    else:
        return render_template('login.html')


@app.route('/')
@login_required
def index():
    return 'Logged in as: ' + current_user.id + 'to logout <a href="' + url_for('logout')+'">click here</a>'

@app.route('/logout')
def logout():
    logout_user()
    return 'Logged out'

app.run(debug=True)