from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Route to check if server is running
@app.route("/")
def home():
    return "Python backend is running ✅"

# Route for sentiment analysis
@app.route("/analyze", methods=["POST"])
def analyze_sentiment():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Hugging Face API call
    HF_API_URL = "https://api-inference.huggingface.co/models/tabularisai/multilingual-sentiment-analysis"
    headers = {"Authorization": f"Bearer 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"}

    response = requests.post(HF_API_URL, headers=headers, json={"inputs": text})

    try:
        result = response.json()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
