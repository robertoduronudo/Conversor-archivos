from flask import Flask, render_template, request, send_file
import os
import pandas as pd
import img2pdf
from fpdf import FPDF
from docx import Document

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convertir', methods=['POST'])
def convertir():
    archivo = request.files['archivo']
    extension = request.form['extension']
    tipo = request.form['tipo']

    filename = archivo.filename
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    archivo.save(input_path)

    nombre_salida = os.path.splitext(filename)[0] + f"_convertido.{tipo}"
    output_path = os.path.join(UPLOAD_FOLDER, nombre_salida)

    try:
        if extension == 'pdf' and tipo == 'jpg':
            return "No se puede convertir de PDF a JPG directamente con esta herramienta."
        elif extension == 'jpg' and tipo == 'pdf':
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(input_path))
        elif extension == 'xlsx' and tipo == 'pdf':
            return "No se puede convertir de Excel a PDF directamente con esta herramienta."
        elif extension == 'docx' and tipo == 'pdf':
            return "No se puede convertir de Word a PDF directamente con esta herramienta."
        elif extension == 'csv' and tipo == 'xlsx':
            df = pd.read_csv(input_path)
            df.to_excel(output_path, index=False)
        elif extension == 'xlsx' and tipo == 'csv':
            df = pd.read_excel(input_path)
            df.to_csv(output_path, index=False)
        else:
            return f"No se puede convertir de {extension} a {tipo} con esta herramienta."

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error en la conversión: {str(e)}"

# Solo este bloque debe existir al final del archivo:
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)