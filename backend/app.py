import os
import uuid
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Read Hugging Face token from env
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    print("⚠️ Warning: HF_TOKEN not set. Set HF_TOKEN env var to avoid permission issues.")

HF_API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

# in-memory store for analysis results
analysis_store = {}

@app.route("/")
def home():
    return "Python backend is running ✅"

@app.route("/analyze", methods=["POST"])
def analyze_sentiment():
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

            # Hugging Face can return either:
            # [[{"label":"LABEL_0","score":0.1}, {"label":"LABEL_1","score":0.7}, {"label":"LABEL_2","score":0.2}]]
            # or
            # [[{"label":"positive","score":0.97}, {"label":"neutral","score":0.01}, {"label":"negative","score":0.01}]]

            label = "Neutral"
            confidence = 0.0

            if isinstance(hf_result, list) and isinstance(hf_result[0], list):
                scores = hf_result[0]
                best = max(scores, key=lambda x: x["score"])
                raw_label = best.get("label", "").upper()
                confidence = float(best.get("score", 0.0))

                # Map both styles
                label_map = {
                    "LABEL_0": "Negative",
                    "LABEL_1": "Neutral",
                    "LABEL_2": "Positive",
                    "NEGATIVE": "Negative",
                    "NEUTRAL": "Neutral",
                    "POSITIVE": "Positive"
                }
                label = label_map.get(raw_label, "Neutral")

        except Exception as e:
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

    analysis_id = uuid.uuid4().hex
    analysis_store[analysis_id] = payload

    return jsonify({
        "message": "Analysis complete",
        "redirect": f"/sentiment?analysis_id={analysis_id}",
        "analysis_id": analysis_id
    })

@app.route("/analyze-results", methods=["GET"])
def get_results():
    analysis_id = request.args.get("analysis_id")
    if not analysis_id:
        return jsonify({"error": "analysis_id query param required"}), 400

    result = analysis_store.get(analysis_id)
    if not result:
        return jsonify({"error": "analysis_id not found"}), 404

    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
