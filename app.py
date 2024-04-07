from flask import Flask, render_template, request, redirect, url_for, send_file
from pyresparser import ResumeParser
import os
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_resume(file_path):
    data = ResumeParser(file_path).get_extracted_data()
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('file')

    extracted_data = []
    for file in uploaded_files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            data = process_resume(file_path)
            data['Filename'] = filename
            extracted_data.append(data)

    if extracted_data:
        output_file = 'output_data.csv'
        df = pd.DataFrame(extracted_data)
        df.to_csv(output_file, index=False)
        return send_file(output_file, as_attachment=True)
    else:
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
