from flask import Blueprint, render_template, json, current_app, request, flash, send_file, abort
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
    task_data = get_task_data(task_id)
    if not task_data:
        abort(404)

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
        if generated_file_path:
            # read compiled pdf into memory so temp files can be deleted ASAP before returning
            return_data = io.BytesIO()
            with open(generated_file_path, 'rb') as f:
                return_data.write(f.read())
                return_data.seek(0)
            
            shutil.rmtree(processing_folder, ignore_errors=True)
            return send_file(return_data, "application/pdf", True, task_name+".pdf")
        else:
            shutil.rmtree(processing_folder, ignore_errors=True)
            flash("Something went wrong formatting your submission. Please check the files and try again. Make sure you uploaded all the files, they don't have special characters, and they are in the correct format. If the issue persists please contact your convener.")

    return render_template('task_format/upload.html', task_id=task_id, name=task_name, upload_requirements=upload_requirements)


def make_pdf(files, task_name, processing_folder):
    template_file = os.path.join(current_app.root_path, 'static/mako/submission_pdf.tmpl')
    tex_template = Template(filename=template_file)
    tex_text = tex_template.render(files=files, task_name=task_name)
    
    tex_file_path = os.path.join(current_app.root_path, processing_folder)
    tex_file_uri = os.path.join(tex_file_path, "compile.tex")
    with open(tex_file_uri, 'w') as out_file:
        out_file.write(tex_text)

    # run twice to resolve page counts and get cross-references right
    subprocess.run(["pdflatex", "-shell-escape", "-halt-on-error", tex_file_uri], cwd=tex_file_path)
    subprocess.run(["pdflatex", "-shell-escape", "-halt-on-error", tex_file_uri], cwd=tex_file_path)

    generated_file_uri = os.path.join(processing_folder, "compile.pdf")

    if os.path.exists(generated_file_uri):
        return generated_file_uri
    else:
        return None


def get_task_data(task_id=None):
    '''Read the json task data and return it.
    
    Returns all the data by default, or the data for a specific task if 
    `task_id` is provided.
    '''
    tasks_file_url = os.path.join(current_app.root_path, 'static/data/tasks.json')
    all_task_data = json.load(open(tasks_file_url))
    if task_id:
        if task_id in all_task_data.keys():
            return all_task_data[task_id]
        else:
            return None
    
    return all_task_data
    