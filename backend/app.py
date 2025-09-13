from flask import Flask, request, jsonify
from transformers import pipeline
from flask_cors import CORS
import torch

app = Flask(__name__)
CORS(app)


device = 0 if torch.cuda.is_available() else -1
classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    device=device,
    return_all_scores=True
)
threshold = 0.7

def analyze_toxicity(text):
    if not text or len(text.strip()) == 0:
        return {"is_toxic": False, "scores": {}, "toxic_labels": [], "confidence": 0.0}

    results = classifier(text)
    toxic_labels = []
    scores = {}
    max_score = 0.0

    for item in results[0]:
        label = item['label']
        score = item['score']
        scores[label] = score
        if score >= threshold and label.lower() != "not toxic":
            toxic_labels.append(label)
            max_score = max(max_score, score)

    is_toxic = len(toxic_labels) > 0
    return {
        "is_toxic": is_toxic,
        "confidence": max_score,
        "toxic_labels": toxic_labels,
        "scores": scores
    }

# REST API endpoint for toxicity detection
@app.route("/")
def home():
    return "Toxicity detection API is running. Use /api/detect or /api/ask endpoints."

@app.route("/api/detect", methods=["POST"])
def api_detect():
    data = request.get_json()
    text = data.get("text", "")
    result = analyze_toxicity(text)
    return jsonify(result)

# REST API endpoint for simple Q&A
@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json()
    question = data.get("question", "")
    # Simple rules -- expand as needed
    if "model" in question.lower():
        answer = "This uses 'unitary/toxic-bert' from HuggingFace Transformers."
    elif "threshold" in question.lower():
        answer = f"The classification threshold is set at {threshold}."
    else:
        answer = "Ask about the model, threshold, or how toxicity is detected."
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
