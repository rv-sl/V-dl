from flask import Flask, jsonify, request
from flask_cors import CORS
from task_m import all_tasks, add_task, add_task_list  # You must define these in task_m.py

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello from Koyeb'

@app.route('/add-task', methods=['POST'])
def add_single_task():
    data = request.json
    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    add_task(data)
    return jsonify({"message": "Task added", "task": data}), 200

@app.route('/add-tasks', methods=['POST'])
def add_multiple_tasks():
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of JSON objects"}), 400

    add_task_list(data)
    return jsonify({"message": f"{len(data)} tasks added"}), 200

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(all_tasks()), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
