from flask import Flask, render_template, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://mac@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app,db) # link the Flask application and SQLAlchemy database instance together

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False, default=False)
  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'



@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']  #fetches the JSON body sent, in this case fetches a dict with key 'description'
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    # todo instance we won't be available after closing sesion so we need to persist it:
    body['description'] = todo.description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close() # return connections to the connection pool at the end of each session
  if error:
    abort(400)
  else:
    return jsonify(body)  # return JSON data to the client


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
#this route is also grabbing the id of the existing todo item that we are going to change the completed status to
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    todo = Todo.query.get(todo_id) #grab the target todo item
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
    #this will grab a fresh list of all the todo items and refresh the entire page of todo items
  return redirect(url_for('index'))
    

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })



@app.route('/')
def index():  #index is the name for the route handler that listens to changes on the index route
  return render_template('index.html', data=Todo.query.order_by('id').all())