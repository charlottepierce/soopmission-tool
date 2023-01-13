from flask import Blueprint, render_template, json, current_app, request, flash

import os, uuid

bp = Blueprint('task_format', __name__, url_prefix='/upload')

@bp.route('/<task_id>', methods=('GET', 'POST'))
def upload_task(task_id):
    # TODO: add 404 page for invalid task id
    # TODO: submit clicked and not all files sent
    task_data = get_task_data(task_id)
    name = task_data['name']
    upload_requirements = task_data['upload_requirements']

    if request.method == 'POST':
        processing_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], uuid.uuid4().hex)
        os.makedirs(processing_folder)
        for requirement in upload_requirements:
            uploaded_file = request.files[requirement]
            _, extension = os.path.splitext(uploaded_file.filename)
            filename = requirement + extension
            uploaded_file.save(os.path.join(processing_folder, filename))
            flash('Got it!')

    return render_template('task_format/upload.html', task_id=task_id, name=name, upload_requirements=upload_requirements)


def get_task_data(task_id=None):
    '''Read the json task data and return it.
    
    Returns all the data by default, or the data for a specific task if 
    `task_id` is provided.
    '''
    tasks_file_url = os.path.join(current_app.root_path, 'static/data/tasks.json')
    all_task_data = json.load(open(tasks_file_url))
    if task_id:
        return all_task_data[task_id]
    
    return all_task_data
    