import os
from flask import Flask, request, jsonify
import requests  # To call Ollama

app = Flask(__name__)

# OLLAMA_HOST should be provided through environment variables for flexibility
# Default value is a placeholder or nip.io-based domain for dynamic IP mapping
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama.<your-ip>.nip.io")  # Replace <your-ip> with the actual IP or domain

@app.route('/')
def home():
    """Health check route to ensure the service is running."""
    return "Inference Service is running!"

@app.route('/inference', methods=['POST'])
def inference():
    """
    Handles inference requests.
    This route accepts POST requests with input data and calls the Ollama model.
    """
    data = request.get_json()
    
    # Call Ollama for inference using the input data
    inference_result = call_ollama_model(data.get("input_data", ""))
    
    return jsonify({"inference_result": inference_result}), 200

def call_ollama_model(input_data):
    """
    Function to call the Ollama model inference endpoint.
    Makes a POST request to the Ollama model running at OLLAMA_HOST.
    """
    # Simulate a call to the Ollama inference endpoint
    response = requests.post(f"{OLLAMA_HOST}/inference", json={"data": input_data})
    
    # Return the JSON response from the Ollama model
    return response.json()

if __name__ == "__main__":
    # Run the Flask app in debug mode on all available IPs (host='0.0.0.0')
    # The port is configurable via the PORT environment variable, defaulting to 8080
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
