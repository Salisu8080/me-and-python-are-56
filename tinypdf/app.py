import os
import subprocess
from flask import Flask, request, render_template, send_file, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def compress_pdf(input_path, output_path, quality="screen"):
    """
    Compress a PDF file using Ghostscript.

    Parameters:
        input_path (str): Path to the input PDF file.
        output_path (str): Path to save the compressed PDF file.
        quality (str): Compression quality. Options: "screen", "ebook", "printer", "prepress".
    """
    gs_command = "gswin64c" if os.name == "nt" else "gs"
    command = [
        gs_command,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",
        f"-sOutputFile={output_path}",
        input_path
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']
        quality = request.form['quality']

        if file:
            # Save the uploaded file
            input_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(input_path)

            # Define the output file path
            output_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{file.filename}")

            # Compress the file
            compress_pdf(input_path, output_path, quality)

            # Provide a download link for the compressed file
            return redirect(url_for('download', filename=f"compressed_{file.filename}"))

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(COMPRESSED_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
