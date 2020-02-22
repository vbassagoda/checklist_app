from flask import Flask, render_template, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://mac@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

#db.create_all()


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
    print(sys.exec_info())
  finally:
    db.session.close() # return connections to the connection pool at the end of each session
  if error:
    abort(400)
  else:
    return jsonify(body)  # return JSON data to the client

@app.route('/')
def index():  #index is the name for the route handler that listens to changes on the index route

  return render_template('index.html', data=Todo.query.all())