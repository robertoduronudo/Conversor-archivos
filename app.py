from flask import Flask, render_template, request, send_file
from fpdf import FPDF
from docx import Document
from PIL import Image
import os
import io
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convertir', methods=['POST'])
def convertir():
    try:
        archivo = request.files['archivo']
        tipo = request.form['tipo']
        nombre = archivo.filename
        extension = os.path.splitext(nombre)[1].lower()
        filepath = os.path.join(UPLOAD_FOLDER, nombre)
        archivo.save(filepath)

        nombre_base = os.path.splitext(nombre)[0]
        output_path = os.path.join(UPLOAD_FOLDER, f"{nombre_base}_convertido.{tipo}")

        # === Conversiones ===

        # TXT a PDF
        if extension == '.txt' and tipo == 'pdf':
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            with open(filepath, 'r') as f:
                for line in f:
                    pdf.cell(200, 10, txt=line.strip(), ln=True)
            pdf.output(output_path)

        # TXT a DOCX
        elif extension == '.txt' and tipo == 'docx':
            doc = Document()
            with open(filepath, 'r') as f:
                for line in f:
                    doc.add_paragraph(line.strip())
            doc.save(output_path)

        # PNG a PDF
        elif extension == '.png' and tipo == 'pdf':
            image = Image.open(filepath)
            image.save(output_path, "PDF", resolution=100.0)

        # PNG a JPG
        elif extension == '.png' and tipo == 'jpg':
            image = Image.open(filepath).convert("RGB")
            image.save(output_path, "JPEG")

        # JPG a PNG
        elif extension == '.jpg' and tipo == 'png':
            image = Image.open(filepath)
            image.save(output_path, "PNG")

        # JPG a PDF
        elif extension == '.jpg' and tipo == 'pdf':
            image = Image.open(filepath).convert("RGB")
            image.save(output_path, "PDF", resolution=100.0)

        # DOCX a TXT
        elif extension == '.docx' and tipo == 'txt':
            doc = Document(filepath)
            with open(output_path, 'w') as f:
                for para in doc.paragraphs:
                    f.write(para.text + '\n')

        # DOCX a PDF (simple)
        elif extension == '.docx' and tipo == 'pdf':
            doc = Document(filepath)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for para in doc.paragraphs:
                pdf.cell(200, 10, txt=para.text.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
            pdf.output(output_path)

        # PDF a TXT
        elif extension == '.pdf' and tipo == 'txt':
            import PyPDF2
            reader = PyPDF2.PdfReader(filepath)
            with open(output_path, 'w') as f:
                for page in reader.pages:
                    f.write(page.extract_text() or '')

        # PDF a DOCX (simple)
        elif extension == '.pdf' and tipo == 'docx':
            import PyPDF2
            reader = PyPDF2.PdfReader(filepath)
            doc = Document()
            for page in reader.pages:
                doc.add_paragraph(page.extract_text() or '')
            doc.save(output_path)

        # PDF a JPG
        elif extension == '.pdf' and tipo == 'jpg':
            from pdf2image import convert_from_path
            images = convert_from_path(filepath)
            images[0].save(output_path, "JPEG")

        # CSV a XLSX
        elif extension == '.csv' and tipo == 'xlsx':
            df = pd.read_csv(filepath)
            df.to_excel(output_path, index=False)

        # XLSX a CSV
        elif extension == '.xlsx' and tipo == 'csv':
            df = pd.read_excel(filepath)
            df.to_csv(output_path, index=False)

        # XLSX a PDF
        elif extension == '.xlsx' and tipo == 'pdf':
            df = pd.read_excel(filepath)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            for i, row in df.iterrows():
                pdf.cell(200, 10, txt=' | '.join(map(str, row.values)), ln=True)
            pdf.output(output_path)

        else:
            return f"No se puede convertir de {extension} a {tipo}"

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error en la conversión: {str(e)}"

if __name__ == '__main__':
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)