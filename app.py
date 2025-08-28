
from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from fpdf import FPDF
import pandas as pd
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convertir', methods=['POST'])
def convertir():
    archivo = request.files['archivo']
    extension = request.form['extension']
    tipo = request.form['tipo']

    if archivo.filename == '':
        return 'No se seleccionó ningún archivo'

    filename = secure_filename(archivo.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    archivo.save(input_path)

    nombre_base = os.path.splitext(filename)[0]
    output_filename = f"{nombre_base}.{extension}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    try:
        if extension == 'pdf' and tipo == 'imagen':
            imagen = Image.open(input_path)
            pdf = FPDF()
            pdf.add_page()
            imagen = imagen.convert('RGB')
            imagen.save(output_path, 'PDF')

        elif extension == 'xlsx' and tipo == 'csv':
            df = pd.read_csv(input_path)
            df.to_excel(output_path, index=False)

        elif extension == 'csv' and tipo == 'xlsx':
            df = pd.read_excel(input_path)
            df.to_csv(output_path, index=False)

        else:
            return f"No se puede convertir de {tipo} a {extension}"

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error en la conversión: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
