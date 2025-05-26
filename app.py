from flask import Flask, render_template, request, send_file
from utils import compare_spec_coa
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    spec_file = request.files['spec_pdf']
    coa_file = request.files['coa_pdf']

    spec_path = os.path.join(UPLOAD_FOLDER, spec_file.filename)
    coa_path = os.path.join(UPLOAD_FOLDER, coa_file.filename)

    spec_file.save(spec_path)
    coa_file.save(coa_path)

    table, excel_path = compare_spec_coa(spec_path, coa_path)

    return render_template('index.html', table=table, excel_link=excel_path)

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
