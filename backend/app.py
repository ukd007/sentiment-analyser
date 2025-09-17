import os
import uuid
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env file
load_dotenv()


app = Flask(__name__)
CORS(app)  # allow cross-origin requests (for dev)

# Read Hugging Face token from env
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    print("Warning: HF_TOKEN not set. Set HF_TOKEN env var to avoid permission issues.")

# CardiffNLP sentiment model
HF_API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

# simple in-memory store for analysis results (keyed by uuid)
analysis_store = {}

@app.route("/")
def home():
    return "Python backend is running ✅"

@app.route("/analyze", methods=["POST"])
def analyze_sentiment():
    """
    Accepts JSON { text: "...multi-line comments..." }
    Splits lines, analyzes each line separately, builds structured payload,
    stores with a uuid and returns redirect + analysis_id.
    """
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    # Split into non-empty lines
    comments = [line.strip() for line in text.splitlines() if line.strip()]
    if not comments:
        return jsonify({"error": "No valid comments found"}), 400

    processed = []
    counts = {"positive": 0, "neutral": 0, "negative": 0}

    for comment in comments:
        try:
            resp = requests.post(HF_API_URL, headers=HEADERS, json={"inputs": comment}, timeout=30)
            resp.raise_for_status()
            hf_result = resp.json()

            # DEBUG: print API result if needed
            # print("HF RESULT:", hf_result)

            # Handle both nested list and flat list responses
            scores = []
            if isinstance(hf_result, list):
                if isinstance(hf_result[0], list):
                    scores = hf_result[0]  # nested list case
                elif isinstance(hf_result[0], dict):
                    scores = hf_result     # flat list case

            if scores:
                best = max(scores, key=lambda x: x.get("score", 0.0))
                raw_label = best.get("label", "")
                confidence = float(best.get("score", 0.0))
                label_map = {"LABEL_0": "Negative", "LABEL_1": "Neutral", "LABEL_2": "Positive"}
                label = label_map.get(raw_label, "Neutral")
            else:
                label, confidence = "Neutral", 0.0

        except Exception as e:
            # log the error
            print(f"Error analyzing comment '{comment}': {e}")
            label, confidence = "Neutral", 0.0

        processed.append({"text": comment, "label": label, "confidence": confidence})

        # Update counts
        if label == "Positive":
            counts["positive"] += 1
        elif label == "Negative":
            counts["negative"] += 1
        else:
            counts["neutral"] += 1

    total = len(processed)
    distribution = {
        "positive": round((counts["positive"] / total) * 100, 1),
        "neutral": round((counts["neutral"] / total) * 100, 1),
        "negative": round((counts["negative"] / total) * 100, 1),
    }

    payload = {
        "distribution": distribution,
        "counts": counts,
        "total": total,
        "comments": processed
    }

    # store and return analysis_id
    analysis_id = uuid.uuid4().hex
    analysis_store[analysis_id] = payload

    return jsonify({
        "message": "Analysis complete",
        "redirect": f"/sentiment?analysis_id={analysis_id}",
        "analysis_id": analysis_id
    })

@app.route("/analyze-results", methods=["GET"])
def get_results():
    """Return stored analysis by id: GET /analyze-results?analysis_id=<id>"""
    analysis_id = request.args.get("analysis_id")
    if not analysis_id:
        return jsonify({"error": "analysis_id query param required"}), 400

    result = analysis_store.get(analysis_id)
    if not result:
        return jsonify({"error": "analysis_id not found"}), 404

    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
