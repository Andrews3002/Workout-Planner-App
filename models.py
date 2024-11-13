from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    workouts = db.relationship('Workout', backref='user', lazy=True, foreign_keys='Workout.user_id')


    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def removeWorkout(self, workout_id):
        alreadyAdded = next((workout for workout in self.workouts if workout.id == workout_id), None)
        if alreadyAdded:
            self.workouts.remove(alreadyAdded)
            db.session.commit()
            return
        return 

    def addPreBuiltWorkout(self, workout_id):
        preBuiltWorkout = Workout.query.filter_by(id=workout_id).first()
        if preBuiltWorkout:
            self.workouts.append(preBuiltWorkout)
            db.session.commit()
        return
    
    def createWorkout(self, exercise_id):
        newWorkout = Workout(exercise_id)
        db.session.add(newWorkout)
        self.workouts.append(newWorkout)
        db.session.commit()
        return
    
    def addExercise(self, workout_id, exercise_id):
        workout = next((workout for workout in self.workouts if workout.id == workout_id), None)
        if workout:
            workout.add_exercise(exercise_id)
            db.session.commit()
            return
        return

    def removeExercise(self, workout_id, exercise_id):
        workout = next((workout for workout in self.workouts if workout.id == workout_id), None)
        if workout:
            workout.remove_exercise(exercise_id)
            db.session.commit()
            return
        return

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    


class Workout(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  exercises = db.relationship('Exercise', backref='workout', lazy=True, foreign_keys='Exercise.workout_id')

  def __init__(self, exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    self.exercises.append(exercise)
  
  def add_exercise(self, exercise_id):
    alreadyAdded = next((exercise for exercise in self.exercises if exercise.id == exercise_id), None)
    if not alreadyAdded:
        exercise = Exercise.query.filter_by(id=exercise_id).first()
        self.exercises.append(exercise)
        db.session.commit()
        return
    flash("Exercise already added to this workout!")
    return 
  
  def remove_exercise(self, exercise_id):
    alreadyAdded = next((exercise for exercise in self.exercises if exercise.id == exercise_id), None)
    if alreadyAdded:
        self.exercises.remove(alreadyAdded)
        db.session.commit()
        return
    return 

  def get_json(self):
   return {
     'id': self.id,
     'name': self.name,
     'exercise_type': self.category,
     'Targeted_body_part': self.body_part,
   }



class Exercise(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  category = db.Column(db.String(255), nullable=False)
  body_part = db.Column(db.String(255), nullable=False)
  workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))
  videoLink = db.Column(db.String(1000), nullable=True)

  def searchResults(q, Radio):
    matching_results = None

    if q == '' and Radio == 0:
        matching_results = Exercise.query.all()

    if q != '' and Radio == 0:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')))

    if q == '' and Radio == 1:
        matching_results = Exercise.query.filter_by(category="Weight_Training")

    if q != '' and Radio == 1:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')), Exercise.category == "Weight_Training")

    if q == '' and Radio == 2:
        matching_results = Exercise.query.filter_by(category="Cardio")

    if q != '' and Radio == 2:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')), Exercise.category == "Cardio")
    
    if q == '' and Radio == 3:
        matching_results = Exercise.query.filter_by(category="Calisthenics")
    
    if q != '' and Radio == 3:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')), Exercise.category == "Calisthenics")
    
    if q == '' and Radio == 4:
        matching_results = Exercise.query.filter_by(body_part="Legs")
    
    if q != '' and Radio == 4:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')), Exercise.body_part == "Legs")

    if q == '' and Radio == 5:
        matching_results = Exercise.query.filter_by(body_part="Back")
    
    if q != '' and Radio == 5:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')), Exercise.body_part == "Back")

    if q == '' and Radio == 6:
        matching_results = Exercise.query.filter_by(body_part="Chest")
    
    if q != '' and Radio == 6:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')), Exercise.body_part == "Chest")

    if q == '' and Radio == 7:
        matching_results = Exercise.query.filter_by(body_part="Shoulders")
    
    if q != '' and Radio == 7:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')), Exercise.body_part == "Shoulders")

    if q == '' and Radio == 8:
        matching_results = Exercise.query.filter_by(body_part="Arms")
    
    if q != '' and Radio == 8:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')), Exercise.body_part == "Arms")

    if q == '' and Radio == 9:
        matching_results = Exercise.query.filter_by(body_part="Abs")
    
    if q != '' and Radio == 9:
        matching_results = Exercise.query.filter(db.or_(Exercise.body_part.ilike(f'%{q}%'), Exercise.name.ilike(f'%{q}%'), Exercise.category.ilike(f'%{q}%')), Exercise.body_part == "Abs")

    return matching_results
  
  def get_json(self):
   return {
     'id': self.id,
     'name': self.name,
     'exercise_type': self.category,
     'Targeted_body_part': self.body_part,
   }