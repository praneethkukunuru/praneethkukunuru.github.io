from flask import Flask, request, jsonify, send_from_directory
import requests
import uuid
import os
from requests.auth import HTTPBasicAuth

app = Flask(__name__, static_folder='static')

# --- Configuration ---
# Set these as environment variables if possible.
CLIENT_ID = os.environ.get('TALKDESK_CLIENT_ID', 'ba239f41d3434c1fa4834452feb42c5f')
CLIENT_SECRET = os.environ.get('TALKDESK_CLIENT_SECRET', '-2KXTTOJ4XeLJ-IqGkKY2rGJtIB9KARvLqhC5tLCtcqQ0mJxr33cfjgmmAcC-oBBFO3xOboXxDmh50qbUf_5qw')
# Token endpoint for QA:
TOKEN_URL = "https://virtualagent.talkdeskqaid.com/oauth/token"
# Generator endpoint for running the template:
GENERATOR_URL = "https://api.talkdeskqa.com/ai-platform/template-based-generator"

# --- Routes ---

# Serve the frontend HTML
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Example endpoint for handling audio uploads (unchanged)
@app.route('/api/test-audio', methods=['POST'])
def test_audio():
    audio = request.files.get('audio')
    features = request.form.get('features')
    if not audio:
        return jsonify({"message": "No audio file received"}), 400
    print("Received Features:", features)
    audio.save("received_audio.wav")
    return jsonify({"message": "Audio received and features logged."})

def get_token():
    """
    Obtain an access token using the client_credentials grant.
    The token endpoint requires Basic authentication using the client_id and client_secret.
    """
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        "grant_type": "client_credentials",
        "scope": "applied-science-functions:invoke ai-generative-function:invoke ai-platform-feedback:send"
    }
    headers = {
        "X-Request-Interaction-ID": "pedro-id",
        "X-Request-Product": "QM_ASSIST"
    }
    response = requests.post(TOKEN_URL, data=data, headers=headers, auth=auth)
    if response.status_code != 200:
        print("Token request error:", response.status_code, response.text)
        return None
    token_data = response.json()
    return token_data.get("access_token")

@app.route('/api/generate', methods=['POST'])
def generate():
    """
    This endpoint receives JSON from the front end with at least a "text" field
    (and optionally a "classes" field). It builds the payload required for the
    Talkdesk template-based generator and calls the generator endpoint using an
    access token obtained from the token endpoint.
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"message": "Missing text input."}), 400

    message_text = data['text']
    classes_value = data.get('classes', '')

    # Build the payload according to the template-based generator format.
    payload = {
        "name": "few_shot_classification",
        "version": "2",
        "parameters": {
            "message": message_text,
            "classes": classes_value
        }
    }

    # Obtain an access token
    token = get_token()
    if not token:
        return jsonify({"message": "Failed to obtain token."}), 401

    headers = {
        "X-Request-Interaction-ID": "VIRTUAL_AGENT",
        "X-Request-Product": "QM_ASSIST",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(GENERATOR_URL, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({
            "message": "Error from external API",
            "details": response.text
        }), response.status_code

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=5001)
