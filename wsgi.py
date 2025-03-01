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
