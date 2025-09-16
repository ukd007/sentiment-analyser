from flask import Flask, request, jsonify, session, redirect, url_for
import requests
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for session storage
CORS(app)

HF_API_URL = "https://api-inference.huggingface.co/models/tabularisai/multilingual-sentiment-analysis"
HEADERS = {"Authorization": f"Bearer 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"}


@app.route("/")
def home():
    return "Python backend is running ✅"


@app.route("/analyze", methods=["POST"])
def analyze_sentiment():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    response = requests.post(HF_API_URL, headers=HEADERS, json={"inputs": text})

    try:
        result = response.json()

        # Save result in session (so sentiment page can fetch it later)
        session["last_result"] = result
        return jsonify({"message": "Analysis complete", "redirect": "/sentiment"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results", methods=["GET"])
def get_results():
    """Provide last analysis results to frontend"""
    result = session.get("last_result", None)
    if not result:
        return jsonify({"error": "No analysis results found"}), 404
    return jsonify(result)


@app.route("/sentiment")
def sentiment_page():
    """Just a placeholder (your HTML frontend will fetch /results)"""
    return "Sentiment page frontend should fetch /results ✅"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
