import os

from flask import Flask, render_template, url_for, json

# the application factory function
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    @app.route('/')
    def index():
        # task_data = json.load(open(url_for('static', filename='data/tasks.json')))
        # print(task_data)
        tasks_file_url = os.path.join(app.root_path, 'static/data/tasks.json')
        task_data = json.load(open(tasks_file_url))
        print(task_data)
        return render_template('index.html', task_data=task_data)

    return app