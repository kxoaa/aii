import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Store chat history per session
chat_sessions = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id", "default")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]

    chat_sessions[session_id].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="openrouter/auto",   # automatically picks best available free model
            messages=chat_sessions[session_id],
        )
        reply = response.choices[0].message.content
        chat_sessions[session_id].append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset():
    data = request.json
    session_id = data.get("session_id", "default")
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)