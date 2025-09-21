from flask import Flask, request, jsonify
from transformers import pipeline
from flask_cors import CORS
import torch
import re
import os
import string
from flask import send_from_directory

# Import enhanced detection modules
try:
    from enhanced_detector import EnhancedToxicityDetector
    from text_normalizer import TextNormalizer
    from sarcasm_detector import SarcasmDetector
    from contextual_analyzer import ContextualAnalyzer
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced features not available: {e}")
    ENHANCED_FEATURES_AVAILABLE = False

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

device = 0 if torch.cuda.is_available() else -1

# Initialize original models
classifier = None
try:
    classifier = pipeline(
        "text-classification",
        model="unitary/toxic-bert",
        device=device,
        top_k=None
    )
    print("Original BERT classifier loaded successfully")
except Exception as e:
    print(f"Original classifier loading error: {e}")

try:
    detoxifier_backup = pipeline("text2text-generation", model="s-nlp/mt0-xl-detox-mpd", device=device)
    print("Detoxification model loaded successfully")
except Exception as e:
    print(f"Detox model loading error: {e}")
    detoxifier_backup = None

threshold = 0.7

# Initialize enhanced detector
enhanced_detector = None
if ENHANCED_FEATURES_AVAILABLE:
    try:
        enhanced_detector = EnhancedToxicityDetector(
            original_classifier=classifier,
            threshold=threshold
        )
        print("Enhanced toxicity detector initialized successfully")
    except Exception as e:
        print(f"Enhanced detector initialization error: {e}")
        enhanced_detector = None

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
    """Enhanced toxicity analysis with fallback to original method"""
    if not text or len(text.strip()) == 0:
        return {"is_toxic": False, "scores": {}, "toxic_labels": [], "confidence": 0.0, "toxic_words": [], "enhanced": False}

    # Try enhanced analysis first
    if enhanced_detector and ENHANCED_FEATURES_AVAILABLE:
        try:
            enhanced_result = enhanced_detector.analyze_toxicity_enhanced(text, CUSTOM_TOXIC_WORDS)
            
            # Convert enhanced result to original format with additional data
            result = {
                "is_toxic": enhanced_result.is_toxic,
                "confidence": enhanced_result.confidence,
                "toxic_labels": enhanced_result.toxic_labels,
                "scores": enhanced_result.scores,
                "toxic_words": enhanced_result.toxic_words,
                "enhanced": True,
                
                # Additional enhanced features
                "normalized_text": enhanced_result.normalized_text,
                "normalization_applied": enhanced_result.normalization_applied,
                "sarcasm_analysis": {
                    "is_sarcastic": enhanced_result.is_sarcastic,
                    "confidence": enhanced_result.sarcasm_confidence,
                    "indicators": enhanced_result.sarcasm_analysis.get("indicators", [])
                },
                "contextual_analysis": {
                    "context_toxicity": enhanced_result.context_toxicity,
                    "risk_factors": enhanced_result.risk_factors,
                    "sequence_labels": enhanced_result.sequence_labels[:5]  # Limit for API response size
                },
                "processing_notes": enhanced_result.processing_notes[-3:],  # Last 3 notes
                "analysis_summary": enhanced_detector.get_analysis_summary(enhanced_result)
            }
            
            return result
            
        except Exception as e:
            print(f"Enhanced analysis failed, falling back to original: {e}")
    
    # Fallback to original analysis
    if not classifier:
        return {"is_toxic": False, "scores": {}, "toxic_labels": [], "confidence": 0.0, "toxic_words": [], "enhanced": False, "error": "No classifier available"}
    
    try:
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
            "enhanced": False
        }
    except Exception as e:
        print(f"Original analysis failed: {e}")
        return {"is_toxic": False, "scores": {}, "toxic_labels": [], "confidence": 0.0, "toxic_words": [], "enhanced": False, "error": str(e)}

def simple_word_replacement(text):
    """Enhanced word replacement using normalization"""
    # Try enhanced normalization first if available
    if ENHANCED_FEATURES_AVAILABLE:
        try:
            normalizer = TextNormalizer()
            normalized_text = normalizer.normalize_text(text)
            # Use normalized text for detection but preserve original structure for replacement
            words_found = find_custom_toxic_words(normalized_text)
        except Exception as e:
            print(f"Enhanced normalization failed in replacement: {e}")
            words_found = find_custom_toxic_words(text)
    else:
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
    """Enhanced detoxification using normalization preprocessing"""
    if detoxifier_backup is None:
        return None
    
    # Preprocess with normalization if available
    processed_text = text
    if ENHANCED_FEATURES_AVAILABLE:
        try:
            normalizer = TextNormalizer()
            processed_text = normalizer.normalize_text(text)
        except Exception as e:
            print(f"Enhanced normalization failed in detoxification: {e}")
            processed_text = text
    
    try:
        result = detoxifier_backup(
            processed_text,
            max_new_tokens=80,
            do_sample=True,
            temperature=0.9,
            top_p=0.8,
            repetition_penalty=1.4
        )
        output = result[0]['generated_text'].strip()
        if output.lower() != processed_text.lower() and len(output) > 3:
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
        if ENHANCED_FEATURES_AVAILABLE:
            answer = "This uses enhanced multi-task detection: 'unitary/toxic-bert' for base detection, advanced text normalization, sarcasm/irony detection, and contextual analysis with sequence labeling."
        else:
            answer = "This uses 'unitary/toxic-bert' for detection and 's-nlp/mt0-xl-detox-mpd' as detoxification model."
    elif "threshold" in question.lower():
        answer = f"The classification threshold is set at {threshold}."
    elif "enhanced" in question.lower() or "features" in question.lower():
        if ENHANCED_FEATURES_AVAILABLE:
            answer = "Enhanced features include: text normalization (emojis, slang, spelling), sarcasm/irony detection, contextual embeddings, sequence labeling, and multi-task learning."
        else:
            answer = "Enhanced features are not currently available. Using basic toxicity detection."
    else:
        answer = "Ask about the model, threshold, enhanced features, or how toxicity is detected."
    return jsonify({"answer": answer})

@app.route("/api/normalize", methods=["POST"])
def api_normalize():
    """New endpoint for text normalization"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({"error": "Enhanced features not available"}), 503
    
    data = request.get_json()
    text = data.get("text", "")
    
    if not text.strip():
        return jsonify({"normalized_text": "", "normalization_info": {}})
    
    try:
        normalizer = TextNormalizer()
        normalized_text = normalizer.normalize_text(text)
        normalization_info = normalizer.get_normalization_info(text)
        
        return jsonify({
            "original_text": text,
            "normalized_text": normalized_text,
            "normalization_applied": normalized_text != text,
            "normalization_info": normalization_info
        })
    except Exception as e:
        return jsonify({"error": f"Normalization failed: {str(e)}"}), 500

@app.route("/api/detect_sarcasm", methods=["POST"])
def api_detect_sarcasm():
    """New endpoint for sarcasm detection"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({"error": "Enhanced features not available"}), 503
    
    data = request.get_json()
    text = data.get("text", "")
    
    if not text.strip():
        return jsonify({"is_sarcastic": False, "confidence": 0.0, "indicators": []})
    
    try:
        sarcasm_detector = SarcasmDetector()
        result = sarcasm_detector.analyze_sarcasm(text)
        
        return jsonify({
            "is_sarcastic": result.is_sarcastic,
            "confidence": result.confidence,
            "confidence_level": sarcasm_detector.get_sarcasm_confidence_level(result.confidence),
            "indicators": result.indicators,
            "score_breakdown": result.score_breakdown
        })
    except Exception as e:
        return jsonify({"error": f"Sarcasm detection failed: {str(e)}"}), 500

@app.route("/api/analyze_context", methods=["POST"])
def api_analyze_context():
    """New endpoint for contextual analysis"""
    if not ENHANCED_FEATURES_AVAILABLE:
        return jsonify({"error": "Enhanced features not available"}), 503
    
    data = request.get_json()
    text = data.get("text", "")
    
    if not text.strip():
        return jsonify({"overall_toxicity": 0.0, "sequence_labels": [], "risk_factors": []})
    
    try:
        contextual_analyzer = ContextualAnalyzer()
        result = contextual_analyzer.analyze_text(text)
        
        # Limit sequence labels for API response
        limited_sequence_labels = [
            {
                "token": token.token,
                "position": token.position,
                "label": token.label.value,
                "confidence": token.confidence
            }
            for token in result.sequence_labels[:20]  # Limit to first 20 tokens
        ]
        
        return jsonify({
            "overall_toxicity": result.overall_toxicity,
            "sequence_labels": limited_sequence_labels,
            "contextual_features": {k: v for k, v in result.contextual_features.items() if isinstance(v, (int, float, bool))},
            "risk_factors": result.risk_factors,
            "attention_weights": result.attention_weights[:20] if result.attention_weights else []
        })
    except Exception as e:
        return jsonify({"error": f"Contextual analysis failed: {str(e)}"}), 500

@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check endpoint with feature availability"""
    health_status = {
        "status": "healthy",
        "features": {
            "basic_detection": classifier is not None,
            "detoxification": detoxifier_backup is not None,
            "enhanced_features": ENHANCED_FEATURES_AVAILABLE and enhanced_detector is not None,
            "text_normalization": ENHANCED_FEATURES_AVAILABLE,
            "sarcasm_detection": ENHANCED_FEATURES_AVAILABLE,
            "contextual_analysis": ENHANCED_FEATURES_AVAILABLE
        },
        "models": {
            "toxicity_classifier": "unitary/toxic-bert" if classifier else None,
            "detoxification": "s-nlp/mt0-xl-detox-mpd" if detoxifier_backup else None
        },
        "threshold": threshold
    }
    
    if ENHANCED_FEATURES_AVAILABLE and enhanced_detector:
        health_status["enhanced_model_versions"] = enhanced_detector.model_versions
    
    return jsonify(health_status)

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

