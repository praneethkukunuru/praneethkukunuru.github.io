from flask import Flask, request, jsonify, send_from_directory
import requests
import uuid

app = Flask(__name__, static_folder='static')

# Serve the frontend HTML
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Existing endpoint to handle audio uploads (unchanged)
@app.route('/api/test-audio', methods=['POST'])
def test_audio():
    audio = request.files.get('audio')
    features = request.form.get('features')

    if not audio:
        return jsonify({"message": "No audio file received"}), 400

    print("Received Features:", features)
    audio.save("received_audio.wav")
    return jsonify({"message": "Audio received and features logged."})

# Updated endpoint that dynamically builds the payload
@app.route('/api/generate', methods=['POST'])
def generate():
    # Expecting JSON with "text" and (optionally) "classes"
    data = request.get_json()
    # print(data)
    if not data or 'text' not in data:
        return jsonify({"message": "Missing text input."}), 400

    # Use the key "text" (from the front end) as the message
    message_text = data['text']
    # Get the classes from the JSON (if not provided, default to an empty string)
    classes_value = data.get('classes', '')

    # Build the payload for the external API call.
    payload = {
        "name": "few_shot_classification",
        "version": "2",
        "parameters": {
            "message": message_text,
            "classes": classes_value
        }
    }
    print(payload)


    # Build the required headers
    headers = {
        'X-Request-Product': 'AGENT_ASSIST',  # Adjust as needed
        'X-Request-Interaction-ID': str(uuid.uuid4()),  # Unique ID for this request
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer 123'  # Replace with your actual token if needed
    }

    # Make the external API call to the Talkdesk endpoint
    external_api_url = "https://api.talkdeskstg.com/ai-platform/template-based-generator"
    response = requests.post(external_api_url, json=payload, headers=headers)

    # Check for errors and return the API response
    if response.status_code != 200:
        return jsonify({
            "message": "Error from external API",
            "details": response.text
        }), response.status_code

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=5001)
