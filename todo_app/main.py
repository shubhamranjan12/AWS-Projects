import os
import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

NFS_DIR = '/mnt/efs'
TODO_FILE = os.path.join(NFS_DIR, 'todos.txt')
todos = []
todo_id_counter = 1


def load_todos():
    global todos, todo_id_counter
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            try:
                todos_data = json.load(f)
                todos = todos_data.get('todos', [])
                todo_id_counter = todos_data.get('todo_id_counter', 1)
            except Exception:
                todos = []
                todo_id_counter = 1
    else:
        todos = []
        todo_id_counter = 1


def save_todos():
    with open(TODO_FILE, 'w') as f:
        json.dump({'todos': todos, 'todo_id_counter': todo_id_counter}, f)


# Load todos at startup
load_todos()


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/todos', methods=['GET'])
def get_todos():
    load_todos()
    return jsonify(todos)


@app.route('/todos', methods=['POST'])
def create_todo():
    global todo_id_counter
    data = request.get_json()
    todo = {
        "id": todo_id_counter,
        "task": data.get("task"),
        "completed": False
    }
    todos.append(todo)
    todo_id_counter += 1
    save_todos()
    return jsonify(todo), 201


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['task'] = data.get("task", todo["task"])
            todo['completed'] = data.get("completed", todo["completed"])
            save_todos()
            return jsonify(todo)
    return jsonify({"error": "Todo not found"}), 404


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos()
    return jsonify({"message": "Todo deleted"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
