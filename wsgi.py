import os, csv, sys, click
from main import app, create_user, get_all_users, get_all_users_json, db
from models import*

@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    db.create_all()
    
    with open('static/exercises.csv', newline='', encoding='utf8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            exercise = Exercise(id=row['id'], name=row['name'], category=row['exercise_type'], body_part=row['Targeted_body_part'], videoLink=row['Video_Link'])
            db.session.add(exercise)
    create_user('bob', 'bobpass')
    create_user('2', '2')
    user = User.query.filter_by(username='bob').first()
    user.createWorkout(1)
    workout = next((workout for workout in user.workouts if workout.id == 1), None)
    workout.add_exercise(2)
    workout.add_exercise(3)
    workout.add_exercise(4)
    workout.add_exercise(5)
    user.createWorkout(6)
    workout = next((workout for workout in user.workouts if workout.id == 2), None)
    workout.add_exercise(7)
    workout.add_exercise(8)
    workout.add_exercise(9)
    workout.add_exercise(10)
    user.createWorkout(11)
    workout = next((workout for workout in user.workouts if workout.id == 3), None)
    workout.add_exercise(12)
    workout.add_exercise(13)
    workout.add_exercise(14)
    workout.add_exercise(15)
    db.session.commit()
    print('database intialized')

@app.cli.command('show-exercises', help="shows a list of all exercises")
def show_exercises():
    exercises = Exercise.query.all()
    for exercise in exercises:
        print(f"id = {exercise.id}, name = {exercise.name}, category = {exercise.category}, body part = {exercise.body_part}, videoLink = {exercise.videoLink}")
    return

@app.cli.command('show-workouts', help="shows a list of all workouts fo a user")
@click.argument("username")
def show_workouts(username):
    user = User.query.filter_by(username=username).first()
    if user:
        for workout in user.workouts:
            for exercise in workout.exercises:
                print(f"id = {exercise.id}, name = {exercise.name}, category = {exercise.category}, body part = {exercise.body_part}, videoLink = {exercise.videoLink}")
    return


@app.cli.command("create", help="Creates a user")
@click.argument("username", default="bob")
@click.argument("password", default="bobpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

@app.cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())
