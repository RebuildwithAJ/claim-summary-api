from flask import Flask, request, jsonify
import requests
import pdfplumber
from fpdf import FPDF
import os

app = Flask(__name__)

@app.route("/process_estimate", methods=["POST"])
def process_estimate():
    data = request.get_json()
    file_url = data.get("file_url")
    claim_number = data.get("claim_number", "Unknown")
    file_name = data.get("file_name")

    pdf_path = f"/tmp/{file_name}"
    r = requests.get(file_url)
    with open(pdf_path, "wb") as f:
        f.write(r.content)

    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    keywords = ["starter", "vent", "ridge", "flashing", "drip edge"]
    found_items = [line for line in full_text.split("\n") if any(k in line.lower() for k in keywords)]

    summary_path = f"/tmp/Summary_{claim_number}.pdf"
    pdf_output = FPDF()
    pdf_output.add_page()
    pdf_output.set_font("Arial", size=12)
    pdf_output.cell(0, 10, f"Supplement Summary – Claim {claim_number}", ln=True)
    pdf_output.ln(10)
    for line in found_items:
        pdf_output.multi_cell(0, 10, f"- {line.strip()}")

    pdf_output.output(summary_path)

    return jsonify({
        "summary_pdf_url": f"https://yourdomain.com/summaries/Summary_{claim_number}.pdf"
    })

if __name__ == "__main__":
    app.run(debug=True)
