from flask import Flask, jsonify, render_template, request
from nlp_processor import analyze

app = Flask(__name__)
MAX_CHARS = 20000
MIN_WORDS = 20


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/extract", methods=["POST"])
def extract_route():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if len(text.split()) < MIN_WORDS:
        return jsonify({"error": f"Enter at least {MIN_WORDS} words to analyze."}), 400
    if len(text) > MAX_CHARS:
        return jsonify({"error": f"Keep the text under {MAX_CHARS} characters."}), 400
    return jsonify(analyze(text))


if __name__ == "__main__":
    app.run(debug=True, port=5050)