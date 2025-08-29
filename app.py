import os
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from img2pdf import convert as img2pdf_convert

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "archivo" not in request.files:
            return "No se encontró el archivo en la solicitud."
        
        archivo = request.files["archivo"]
        formato_destino = request.form.get("formato")

        if archivo.filename == "":
            return "No se seleccionó ningún archivo."
        
        if archivo and formato_destino == "pdf":
            filename = secure_filename(archivo.filename)
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            archivo.save(input_path)

            output_filename = os.path.splitext(filename)[0] + ".pdf"
            output_path = os.path.join(UPLOAD_FOLDER, output_filename)

            try:
                with open(input_path, "rb") as f_input, open(output_path, "wb") as f_output:
                    f_output.write(img2pdf_convert(f_input))
                return send_file(output_path, as_attachment=True)
            except Exception as e:
                return f"Error en la conversión: {str(e)}"

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)