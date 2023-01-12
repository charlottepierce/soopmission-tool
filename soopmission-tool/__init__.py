import os

from flask import Flask, render_template

# the application factory function
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from . import task_format
    app.register_blueprint(task_format.bp)

    @app.route('/')
    def index():
        task_data = task_format.get_task_data()
        return render_template('index.html', task_data=task_data)

    return app