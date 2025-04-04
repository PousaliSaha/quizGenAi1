from flask import Flask, request, jsonify
import fitz  # PyMuPDF for extracting text from PDFs
import random
import os
from flask_cors import CORS  # Fixes frontend connection issue

app = Flask(__name__)
CORS(app)  # Allows frontend to connect to backend

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text if text else None
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

def generate_mcqs(text, num_questions=5):
    """Generates multiple MCQ questions."""
    sentences = [s.strip() for s in text.split(".") if len(s.split()) > 5]
    mcqs = []

    for _ in range(min(num_questions, len(sentences))):
        sentence = random.choice(sentences)
        words = sentence.split()
        if len(words) > 5:
            correct_answer = random.choice(words)
            wrong_answers = random.sample([w for w in words if w != correct_answer], min(3, len(words) - 1))
            options = [correct_answer] + wrong_answers
            random.shuffle(options)
            question = sentence.replace(correct_answer, "______")
            mcqs.append({
                "question": question,
                "options": options,
                "answer": correct_answer
            })
    return mcqs

def generate_theoretical_questions(text, num_questions=5):
    """Generates multiple theoretical questions."""
    sentences = [s.strip() for s in text.split(".") if len(s.split()) > 5]
    theoretical_questions = [f"What is the meaning of: '{s}?'" for s in random.sample(sentences, min(num_questions, len(sentences)))]
    return theoretical_questions

@app.route("/upload", methods=["POST"])
def upload_pdf():
    """Handles PDF upload and generates questions."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        text = extract_text_from_pdf(pdf_path)
        if not text:
            return jsonify({"error": "Failed to extract text"}), 500

        mcqs = generate_mcqs(text, num_questions=5)
        theory_questions = generate_theoretical_questions(text, num_questions=5)

        return jsonify({
            "mcqs": mcqs,
            "theoretical_questions": theory_questions
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
