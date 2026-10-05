"""
Flask Backend Application for AI Laptop Selection Chatbot Expert System
Provides REST APIs for conversational chatbot, recommendations, comparisons, and catalog inspection.
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, session
from database import init_db, get_all_laptops, get_laptop_by_id
from chatbot import ChatbotSession
from expert_system import InferenceEngine

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory store for user sessions: session_id -> ChatbotSession instance
user_sessions = {}

# Initialize Inference Engine
inference_engine = InferenceEngine()


def get_or_create_session():
    """Retrieves or creates a stateful ChatbotSession for the current client."""
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    sid = session["session_id"]
    if sid not in user_sessions:
        user_sessions[sid] = ChatbotSession(sid)
    return user_sessions[sid]


@app.route("/")
def index():
    """Renders the main chatbot interactive interface."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Main conversational endpoint.
    Receives user message and returns expert system response,
    suggestions, recommendations, and comparison payloads.
    """
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message", "")
        bot_session = get_or_create_session()
        response = bot_session.handle_message(message)
        return jsonify(response)
    except Exception as e:
        return jsonify({
            "reply": "An unexpected error occurred while processing your request. Please try again or type 'restart'.",
            "error": str(e),
            "status": "error",
            "options": ["restart"]
        }), 500


@app.route("/recommend", methods=["POST"])
def direct_recommend():
    """
    Direct API endpoint to get laptop recommendations from raw specifications.
    Useful for testing or direct API integrations.
    """
    try:
        req_data = request.get_json(silent=True) or {}
        top_n = req_data.get("top_n", 3)
        res = inference_engine.recommend(req_data, top_n=top_n)
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/compare", methods=["POST"])
def compare():
    """
    Compares two laptops side-by-side using the expert system inference engine.
    Receives { "id1": int, "id2": int }.
    """
    try:
        data = request.get_json(silent=True) or {}
        id1 = data.get("id1")
        id2 = data.get("id2")

        if not id1 or not id2:
            return jsonify({"error": "Both id1 and id2 are required"}), 400

        result = inference_engine.compare_laptops(int(id1), int(id2))
        if not result:
            return jsonify({"error": "One or both laptops not found"}), 404

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset():
    """Resets the current conversation state and returns welcome greeting."""
    try:
        bot_session = get_or_create_session()
        welcome = bot_session.reset()
        return jsonify(welcome)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/laptops", methods=["GET"])
def list_laptops():
    """Returns all laptops stored in the SQLite database."""
    try:
        laptops = get_all_laptops()
        return jsonify({
            "count": len(laptops),
            "laptops": laptops
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/laptop/<int:laptop_id>", methods=["GET"])
def get_laptop(laptop_id):
    """Returns details of a specific laptop by ID."""
    try:
        laptop = get_laptop_by_id(laptop_id)
        if not laptop:
            return jsonify({"error": "Laptop not found"}), 404
        return jsonify(laptop)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 AI Laptop Selection Chatbot starting on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
