import os

from flask import Flask, render_template, send_from_directory

# the application factory function
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER='uploads',
        MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    )
    # TODO override with production config when available

    # ensure the uploads folder exists
    try:
        os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']))
    except:
        pass

    from . import task_format
    app.register_blueprint(task_format.bp)

    @app.route('/')
    def index():
        task_data = task_format.get_task_data()
        return render_template('index.html', task_data=task_data)

    @app.route('/robots.txt')
    def robots_file():
        return send_from_directory("static", "robots.txt")

    return app