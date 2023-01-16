from flask import Blueprint, render_template, json, current_app, request, flash
from mako.template import Template

import os, uuid, subprocess

bp = Blueprint('task_format', __name__, url_prefix='/upload')

class SubmissionFile(object):
    def __init__(self, name, file_path, type, extension):
        self.name = name
        self.file_path = file_path
        self.type = type
        self.extension = extension


@bp.route('/<task_id>', methods=('GET', 'POST'))
def upload_task(task_id):
    # TODO: add 404 page for invalid task id
    # TODO: submit clicked and not all files sent
    task_data = get_task_data(task_id)
    task_name = task_data['name']
    upload_requirements = task_data['upload_requirements']

    if request.method == 'POST':
        # processing_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], uuid.uuid4().hex)
        processing_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], "1") # hard-code for a minute while working so you don't have to keep switching folders
        try:
            os.makedirs(processing_folder)
        except:
            pass
        files = []
        for requirement in upload_requirements:
            uploaded_file = request.files[requirement]
            _, extension = os.path.splitext(uploaded_file.filename)
            filename = requirement + extension
            filepath = os.path.join(processing_folder, filename)
            files.append(SubmissionFile(requirement, filepath, upload_requirements[requirement]["type"], extension))
            uploaded_file.save(filepath)
            make_pdf(files, task_name, processing_folder)
            flash('Got it!')
            # TODO: return pdf to user, named based on task
            # TODO: remove temp files 

    return render_template('task_format/upload.html', task_id=task_id, name=task_name, upload_requirements=upload_requirements)


def make_pdf(files, task_name, processing_folder):
    # TODO: detect and handle when tex compile fails
    # TODO: add in actual task content
    template_file = os.path.join(current_app.root_path, 'static/mako/submission_pdf.tmpl')
    tex_template = Template(filename=template_file)
    tex_text = tex_template.render(files=files, task_name=task_name)
    
    out_file_path = os.path.join(current_app.root_path, processing_folder)
    out_file_uri = os.path.join(out_file_path, "compile.tex")
    with open(out_file_uri, 'w') as out_file:
        out_file.write(tex_text)

    # run twice to resolve page counts
    subprocess.run(["pdflatex", "-shell-escape", out_file_uri], cwd=out_file_path)
    subprocess.run(["pdflatex", "-shell-escape", out_file_uri], cwd=out_file_path)


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
    