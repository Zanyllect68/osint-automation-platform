from flask import Flask, request, send_file
import os
import subprocess
import uuid
import zipfile

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf():
    # ID único
    job_id = str(uuid.uuid4())
    input_pdf = f"/tmp/{job_id}.pdf"
    output_prefix = f"/tmp/{job_id}"

    # guardar PDF
    with open(input_pdf, "wb") as f:
        f.write(request.data)

    # convertir PDF → imágenes
    subprocess.run([
        "pdftoppm",
        "-png",
        "-r", "300",
        input_pdf,
        output_prefix
    ], check=True)

    # crear zip con imágenes
    zip_path = f"/tmp/{job_id}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir("/tmp"):
            if file.startswith(job_id) and file.endswith(".png"):
                zipf.write(f"/tmp/{file}", arcname=file)

    return send_file(zip_path, mimetype='application/zip')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)