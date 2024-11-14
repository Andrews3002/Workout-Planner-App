import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from functools import wraps
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (JWTManager, create_access_token, get_jwt_identity, jwt_required, current_user, set_access_cookies,
unset_jwt_cookies, verify_jwt_in_request)

from models import User, Workout, Exercise, db

def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          user_id = get_jwt_identity()
          current_user = User.query.get(user_id)
          is_authenticated = True
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)

def create_app():
    app = Flask(__name__, static_url_path='/static')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///your_database_name.db"
    app.config['SECRET_KEY'] = "secret key"
    app.config['ENV'] = "PRODUCTION" 
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 7
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_SECURE"] = True
    app.config["JWT_SECRET_KEY"] = "super-secret"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    
    add_auth_context(app)
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()
jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(identity):
    user = User.query.filter_by(username=identity).one_or_none()
    if user:
        return user.id
    return None

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)

@jwt.invalid_token_loader
@jwt.invalid_token_loader
def custom_unauthorized_response(error):
    return render_template('401.html', error=error), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return render_template('401.html'), 401 


def login_required(required_class):
  def wrapper(f):
      @wraps(f)
      @jwt_required() 
      def decorated_function(*args, **kwargs):
        user = required_class.query.get(get_jwt_identity())
        if user.__class__ != required_class: 
            return jsonify(message='Invalid user role'), 403
        return f(*args, **kwargs)
      return decorated_function
  return wrapper

def create_user(username, password):
    newuser = User(username=username, password=password)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_user(id):
    return User.query.get(id)

def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        db.session.add(user)
        return db.session.commit()
    return None

@app.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')
    
@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_action():
    response = None
    username = request.form['username']
    password = request.form['password']
    token = login(username, password)
    if token == None:
        flash('Incorrect username or password given'), 401
        response = redirect(url_for('login_page'))
        return response
    else:
        flash('Login Successful')
        response = redirect(url_for('index_page'))
        set_access_cookies(response, token) 
        return response

def login(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    return create_access_token(identity=username)
  return None

@app.route('/signup-page', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route("/signup", methods=['POST'])
def signup_action():
  response = None
  try:
    username = request.form['username']
    password = request.form['password']
    user = create_user(username, password)
    response = redirect(url_for('login_page'))
    flash('Account created')
  except IntegrityError:
    flash('Username already exists')
    response = redirect(url_for('signup_page'))
  return response

@app.route('/home', methods=['GET'])
@jwt_required()
def index_page():
    username = get_jwt_identity()
    return render_template('index.html', username=username)


@app.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(url_for('login_page')) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response


@app.route('/browseExercises_page/', methods=['GET'])
@app.route('/browseExercises_page/add/<int:exercise_id>', methods=['GET'])
@app.route('/browseExercises_page/add/<int:exercise_id>/<int:workout_id>', methods=['GET'])
@app.route('/browseExercises_page/remove/<int:workout_id>', methods=['GET'])
@app.route('/browseExercises_page/newWorkout/<int:intNewWorkout>/<exercise_id>', methods=['GET'])
@jwt_required()
def browseExercises_page(workout_id=None, exercise_id=None, intNewWorkout=0):

    q = request.args.get('q', default='', type=str)

    Radio = request.args.get('Radio', default=0, type=int)

    exercises = Exercise.searchResults(q, Radio)

    if intNewWorkout == 1:
        new_workout = True
    else:
        new_workout = False
        
    return render_template('browseExercises.html', exercises=exercises, workout_id=workout_id, exercise_id=exercise_id, new_workout=new_workout, q=q, Radio=Radio)

@app.route('/addExercise/<int:exercise_id>/<int:workout_id>', methods=['POST'])
@jwt_required()
def addExercise_action(exercise_id, workout_id):
    current_user.addExercise(workout_id, exercise_id)
    return redirect(url_for('browseExercises_page'))

@app.route('/removeExercise/<int:exercise_id>/<int:workout_id>', methods=['POST'])
@jwt_required()
def removeExercise_action(exercise_id, workout_id):
    current_user.removeExercise(workout_id, exercise_id)
    return redirect(url_for('manageWorkouts_page'))

@app.route('/removeWorkout/<int:workout_id>', methods=['POST'])
@jwt_required()
def removeWorkout_action(workout_id):
    current_user.removeWorkout(workout_id)
    return redirect(url_for('browseExercises_page'))

@app.route('/createWorkout/<int:exercise_id>', methods=['POST'])
@jwt_required()
def createWorkout_action(exercise_id):
    current_user.createWorkout(exercise_id)
    return redirect(url_for('browseExercises_page'))

@app.route('/manageWorkouts_page', methods=['GET'])
@app.route('/remove/<int:exercise_id>/<int:workout_id>', methods=['GET'])
@jwt_required()
def manageWorkouts_page(exercise_id=None, workout_id=None):
    return render_template('manageWorkouts.html', exercise_id=exercise_id, workout_id=workout_id)

@app.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@app.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

'''
API Routes
'''
@app.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@app.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@app.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})

@app.route('/users', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    return redirect(url_for('get_user_page'))

@app.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    user = create_user(data['username'], data['password'])
    return jsonify({'message': f"user {user.username} created with id {user.id}"})

@app.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')

@app.route('/images', methods=['GET'])
@app.route("/images/<string:filename>", methods=['GET'])
def images_access(filename):
  return send_from_directory('images', filename)

