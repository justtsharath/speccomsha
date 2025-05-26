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

# Assume your Flask app ('app') is defined above this
# For example:
# from flask import Flask, send_file
# app = Flask(__name__)
#
# @app.route('/')
# def hello():
#     return "Hello from Flask!"
#
# @app.route('/download/<filename>') # Example route using send_file
# def download_file(filename):
#    # IMPORTANT: Ensure 'filename' is safe and points to an actual, intended file.
#    # Add security checks here to prevent directory traversal attacks.
#    # For example, ensure the filename is within a specific allowed directory.
#    # For simplicity, this example assumes 'filename' is just the name of a file
#    # in the same directory or a pre-defined safe path.
#    try:
#        return send_file(filename, as_attachment=True)
#    except FileNotFoundError:
#        return "File not found", 404

# The critical change is in the app.run() call:
if __name__ == '__main__':
    # Disable the Werkzeug reloader and debugger when running in an environment
    # like Streamlit, which manages its own execution.
    # The reloader (part of debug=True) causes the signal error.
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000) # MODIFIED LINE
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
