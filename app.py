from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static')

# Route to serve the frontend HTML
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Route to handle audio and feature toggles
@app.route('/api/test-audio', methods=['POST'])
def test_audio():
    audio = request.files.get('audio')
    features = request.form.get('features')

    if not audio:
        return jsonify({"message": "No audio file received"}), 400

    # Log the received features and save the audio file
    print("Received Features:", features)
    audio.save("received_audio.wav")

    # Respond back to the frontend
    return jsonify({"message": "Audio received and features logged."})

if __name__ == '__main__':
    app.run(debug=True)
