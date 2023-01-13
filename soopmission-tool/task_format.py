from flask import Blueprint, render_template, json, current_app, request, flash
from mako.template import Template

import os, uuid

bp = Blueprint('task_format', __name__, url_prefix='/upload')

@bp.route('/<task_id>', methods=('GET', 'POST'))
def upload_task(task_id):
    # TODO: add 404 page for invalid task id
    # TODO: submit clicked and not all files sent
    task_data = get_task_data(task_id)
    task_name = task_data['name']
    upload_requirements = task_data['upload_requirements']

    if request.method == 'POST':
        processing_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], uuid.uuid4().hex)
        os.makedirs(processing_folder)
        for requirement in upload_requirements:
            uploaded_file = request.files[requirement]
            _, extension = os.path.splitext(uploaded_file.filename)
            filename = requirement + extension
            uploaded_file.save(os.path.join(processing_folder, filename))
            make_pdf(upload_requirements, processing_folder, task_name)
            flash('Got it!')

    return render_template('task_format/upload.html', task_id=task_id, name=task_name, upload_requirements=upload_requirements)


def make_pdf(upload_requirements, processing_folder, task_name):
    template_file = os.path.join(current_app.root_path, 'static/mako/submission_pdf.tmpl')
    tex_template = Template(filename=template_file)
    tex_text = tex_template.render(upload_requirements=upload_requirements, task_name=task_name)
    
    out_file_name = task_name + ".tex"
    with open(os.path.join(current_app.root_path, processing_folder, out_file_name), 'w') as out_file:
        out_file.write(tex_text)


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
    