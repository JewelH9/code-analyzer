# app.py (updated)
from analyzer.executor import execute_code
from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import analyze_code   # ← Import our engine

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


@app.route('/analyze', methods=['POST'])
def analyze():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body received"}), 400

    code = data.get("code", "")
    language = data.get("language", "python")

    if not code.strip():
        return jsonify({"error": "Code cannot be empty"}), 400

    # 🔥 Now calling the real engine (even if it returns placeholders)
    result = analyze_code(code, language)

    return jsonify(result), 200

@app.route('/execute', methods=['POST'])
def execute():
    """
    Endpoint: POST /execute
    Body: { "code": "...", "language": "python" }
    
    Returns:
    {
        "success":      true/false,
        "output":       "program output",
        "error":        "error message or null",
        "exec_time_ms": 12.34,
        "timed_out":    false
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body"}), 400

    code     = data.get("code", "")
    language = data.get("language", "python")

    if not code.strip():
        return jsonify({"error": "Code cannot be empty"}), 400

    result = execute_code(code, language)
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)