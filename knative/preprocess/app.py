import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    """Health check route to ensure the preprocess service is running."""
    return "Preprocess Service is running!"

@app.route('/preprocess', methods=['POST'])
def preprocess():
    """
    Endpoint to handle data preprocessing requests.
    This simulates data cleaning or transformation operations.
    Expects input data in JSON format.
    """
    data = request.get_json()  # Get input data from the request body
    
    # Call the data processing logic to clean/transform the input data
    processed_data = data_processing_logic(data)
    
    return jsonify({"processed_data": processed_data}), 200  # Return the processed data

def data_processing_logic(data):
    """
    Placeholder function to implement data preprocessing logic.
    Example: Converts input data to lowercase (basic text cleaning).
    In real cases, this could be more complex (e.g., tokenization, normalization).
    """
    # Basic transformation: Convert input data to lowercase
    return {"processed": data.get("input_data", "").lower()}  # Returns lowercased input data

if __name__ == "__main__":
    # Run the Flask app on all available IPs (host='0.0.0.0') for external access
    # Port is configurable via an environment variable (default is 8080)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
