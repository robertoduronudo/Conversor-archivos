import os
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from PIL import Image
from fpdf import FPDF
import docx
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def convert_file():
    file = request.files['file']
    output_format = request.form['format']

    if not file or output_format == '':
        return "Falta el archivo o el formato de salida", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    name, ext = os.path.splitext(filename)
    ext = ext.lower().strip('.')
    output_filename = f"{name}_converted.{output_format.lower()}"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    try:
        if ext == "pdf" and output_format in ["png", "jpg"]:
            from pdf2image import convert_from_path
            images = convert_from_path(input_path)
            images[0].save(output_path, output_format.upper())

        elif ext == "pdf" and output_format == "txt":
            import fitz  # PyMuPDF
            doc = fitz.open(input_path)
            text = ""
            for page in doc:
                text += page.get_text()
            with open(output_path, "w") as f:
                f.write(text)

        elif ext == "pdf" and output_format == "docx":
            from pdf2docx import Converter
            cv = Converter(input_path)
            cv.convert(output_path)
            cv.close()

        elif ext == "pdf" and output_format == "xlsx":
            import tabula
            dfs = tabula.read_pdf(input_path, pages='all', multiple_tables=True)
            with pd.ExcelWriter(output_path) as writer:
                for i, df in enumerate(dfs):
                    df.to_excel(writer, sheet_name=f'Sheet{i}', index=False)

        elif ext in ["png", "jpg"] and output_format == "pdf":
            img = Image.open(input_path)
            img.convert("RGB").save(output_path, "PDF")

        elif ext == "png" and output_format == "jpg":
            img = Image.open(input_path)
            img.convert("RGB").save(output_path, "JPEG")

        elif ext == "jpg" and output_format == "png":
            img = Image.open(input_path)
            img.save(output_path, "PNG")

        elif ext == "txt" and output_format == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            with open(input_path, 'r') as f:
                for line in f:
                    pdf.cell(200, 10, txt=line.strip(), ln=True)
            pdf.output(output_path)

        elif ext == "docx" and output_format == "pdf":
            from docx2pdf import convert
            convert(input_path, output_path)

        elif ext == "xlsx" and output_format == "pdf":
            df = pd.read_excel(input_path)
            df.to_csv("temp.csv", index=False)
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            with open("temp.csv", 'r') as f:
                for line in f:
                    pdf.cell(200, 10, txt=line.strip(), ln=True)
            pdf.output(output_path)
            os.remove("temp.csv")

        else:
            return f"Conversión de {ext} a {output_format} no soportada.", 400

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error durante la conversión: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=False, host='0.0.0.0', port=port)