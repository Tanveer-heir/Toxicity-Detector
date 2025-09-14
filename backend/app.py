from flask import Flask, request, jsonify
from transformers import pipeline
from flask_cors import CORS
import torch
import re
import os
import string
from flask import send_from_directory

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

device = 0 if torch.cuda.is_available() else -1

classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    device=device,
    top_k=None
)

try:
    detoxifier_backup = pipeline("text2text-generation", model="s-nlp/mt0-xl-detox-mpd", device=device)
except Exception as e:
    print(f"Detox model loading error: {e}")
    detoxifier_backup = None

threshold = 0.7

def load_custom_toxic_words(file_path):
    toxic_words = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    toxic_words.add(word)
    else:
        print(f"Warning: Toxic words file '{file_path}' not found. Using empty list.")
    return toxic_words

def load_word_replacements(file_path):
    replacements = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(',', 1)
                if len(parts) == 2:
                    toxic_word = parts[0].strip().lower()
                    replacement = parts[1].strip()
                    if toxic_word and replacement:
                        replacements[toxic_word] = replacement
    else:
        print(f"Warning: Word replacements file '{file_path}' not found. Using empty replacements.")
    return replacements

CUSTOM_TOXIC_WORDS = load_custom_toxic_words(r"../toxic.txt")

WORD_REPLACEMENTS = load_word_replacements(r"../replacement.txt")

def find_custom_toxic_words(text):
    text_lower = text.lower()
    found_words = set()
    
    text_processed = re.sub(f"[{re.escape(string.punctuation)}]", " ", text_lower)
    
    for word in CUSTOM_TOXIC_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text_processed):
            found_words.add(word)
    
    return list(found_words)

def analyze_toxicity(text):
    if not text or len(text.strip()) == 0:
        return {"is_toxic": False, "scores": {}, "toxic_labels": [], "confidence": 0.0, "toxic_words": []}

    results = classifier(text)
    toxic_labels = []
    scores = {}
    max_score = 0.0

    for item in results[0]:
        label = item["label"]
        score = item["score"]
        scores[label] = score
        if score >= threshold and label.lower() != "not toxic":
            toxic_labels.append(label)
            if score > max_score:
                max_score = score

    toxic_words = find_custom_toxic_words(text)
    is_toxic = len(toxic_labels) > 0 or len(toxic_words) > 0

    return {
        "is_toxic": is_toxic,
        "confidence": max_score,
        "toxic_labels": toxic_labels,
        "scores": scores,
        "toxic_words": toxic_words,
    }

def simple_word_replacement(text):
    words_found = find_custom_toxic_words(text)
    if not words_found:
        return None
    result_text = text
    for word in words_found:
        replacement = WORD_REPLACEMENTS.get(word)
        if replacement:
            pattern = rf"\b{re.escape(word)}\b"
            result_text = re.sub(pattern, replacement, result_text, flags=re.IGNORECASE)
    return result_text

def detoxify_with_backup_model(text):
    if detoxifier_backup is None:
        return None
    try:
        result = detoxifier_backup(
            text,
            max_new_tokens=80,
            do_sample=True,
            temperature=0.9,
            top_p=0.8,
            repetition_penalty=1.4
        )
        output = result[0]['generated_text'].strip()
        if output.lower() != text.lower() and len(output) > 3:
            return output
    except Exception as e:
        print(f"Backup model error: {e}")
    return None

@app.route("/")
def home():
    return "Toxicity detection API is running. Use /api/detect, /api/ask, or /api/detoxify endpoints."

@app.route("/api/detect", methods=["POST"])
def api_detect():
    data = request.get_json()
    text = data.get("text", "")
    result = analyze_toxicity(text)
    return jsonify(result)

@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json()
    question = data.get("question", "")
    if "model" in question.lower():
        answer = "This uses 'unitary/toxic-bert' for detection and 's-nlp/mt0-xl-detox-mpd' as detoxification model."
    elif "threshold" in question.lower():
        answer = f"The classification threshold is set at {threshold}."
    else:
        answer = "Ask about the model, threshold, or how toxicity is detected."
    return jsonify({"answer": answer})

@app.route("/api/detoxify", methods=["POST", "OPTIONS"])
def api_detoxify():
    if request.method == "OPTIONS":
        return '', 200
    data = request.get_json()
    toxic_text = data.get("text", "")
    if not toxic_text.strip():
        return jsonify({"detoxified_text": ""})

    
    replaced_text = simple_word_replacement(toxic_text)
    if replaced_text is not None and replaced_text.lower() != toxic_text.lower():
        return jsonify({"detoxified_text": replaced_text})

    # Then try detoxification model
    detoxified_text = detoxify_with_backup_model(toxic_text)
    if detoxified_text is not None:
        return jsonify({"detoxified_text": detoxified_text})

    return jsonify({"detoxified_text": "Please express your message in a more respectful way."})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                              'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=False, port=8000, host="127.0.0.1", use_reloader=False)

