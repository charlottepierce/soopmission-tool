from flask import Blueprint, render_template, json, current_app, request, flash, send_file
from mako.template import Template

import os
import uuid
import subprocess
import io
import shutil

bp = Blueprint('task_format', __name__, url_prefix='/upload')

class SubmissionFile(object):
    def __init__(self, name, file_path, type, extension):
        self.name = name
        self.file_path = file_path
        self.type = type
        self.extension = extension

    def pygments_lang(self):
        if self.extension == ".cs":
            return "csharp"
        else:
            return "text"


@bp.route('/<task_id>', methods=('GET', 'POST'))
def upload_task(task_id):
    # TODO: add 404 page for invalid task id
    # TODO: submit clicked and not all files sent
    task_data = get_task_data(task_id)
    task_name = task_data['name']
    upload_requirements = task_data['upload_requirements']

    if request.method == 'POST':
        processing_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], uuid.uuid4().hex)
        try:
            os.makedirs(processing_folder)
        except:
            pass
        files = []
        for requirement in upload_requirements:
            uploaded_file = request.files[requirement]
            _, extension = os.path.splitext(uploaded_file.filename)
            filename = requirement.replace(" ", "") + extension
            filepath = os.path.join(processing_folder, filename)
            files.append(SubmissionFile(requirement, filepath, upload_requirements[requirement]["type"], extension))
            uploaded_file.save(filepath)

        generated_file_path = make_pdf(files, task_name, processing_folder)
        # read compiled pdf into memory so temp files can be deleted ASAP before returning
        return_data = io.BytesIO()
        with open(generated_file_path, 'rb') as f:
            return_data.write(f.read())
            return_data.seek(0)
        
        shutil.rmtree(processing_folder, ignore_errors=True)
        return send_file(return_data, "application/pdf", True, task_name+".pdf")

    return render_template('task_format/upload.html', task_id=task_id, name=task_name, upload_requirements=upload_requirements)


def make_pdf(files, task_name, processing_folder):
    # TODO: detect and handle when tex compile fails
    template_file = os.path.join(current_app.root_path, 'static/mako/submission_pdf.tmpl')
    tex_template = Template(filename=template_file)
    tex_text = tex_template.render(files=files, task_name=task_name)
    
    tex_file_path = os.path.join(current_app.root_path, processing_folder)
    tex_file_uri = os.path.join(tex_file_path, "compile.tex")
    with open(tex_file_uri, 'w') as out_file:
        out_file.write(tex_text)

    # run twice to resolve page counts and get cross-references right
    subprocess.run(["pdflatex", "-shell-escape", tex_file_uri], cwd=tex_file_path)
    subprocess.run(["pdflatex", "-shell-escape", tex_file_uri], cwd=tex_file_path)

    generated_file_uri = os.path.join(processing_folder, "compile.pdf")

    return generated_file_uri


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
    