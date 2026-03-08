from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory database
todos = []
todo_id_counter = 1


@app.route("/")
def home():
    return render_template("index.html")


# Get all todos
@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)


# Get a single todo
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            return jsonify(todo)
    return jsonify({"error": "Todo not found"}), 404


# Create a new todo
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

    return jsonify(todo), 201


# Update todo
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()

    for todo in todos:
        if todo['id'] == todo_id:
            todo['task'] = data.get("task", todo["task"])
            todo['completed'] = data.get("completed", todo["completed"])
            return jsonify(todo)

    return jsonify({"error": "Todo not found"}), 404


# Delete todo
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [todo for todo in todos if todo["id"] != todo_id]

    return jsonify({"message": "Todo deleted"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
