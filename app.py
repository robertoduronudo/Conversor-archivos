from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convertir", methods=["POST"])
def convertir():
    if "file" not in request.files:
        return "No se envió ningún archivo", 400

    file = request.files["file"]
    output_format = request.form["output_format"]

    if file.filename == "":
        return "Nombre de archivo vacío", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    name, ext = os.path.splitext(filename)
    output_path = os.path.join(UPLOAD_FOLDER, f"{name}.{output_format}")

    try:
        with Image.open(input_path) as img:
            rgb_img = img.convert("RGB")
            rgb_img.save(output_path, output_format.upper())

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error durante la conversión: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))