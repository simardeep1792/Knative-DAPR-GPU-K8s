import os
from flask import Flask, request, jsonify
import redis
import psycopg2

app = Flask(__name__)

# Redis and PostgreSQL configurations sourced from environment variables
# These variables should be set in your environment or Kubernetes deployment to avoid hardcoding
REDIS_HOST = os.environ.get("REDIS_HOST", "redis-service")  # Redis service host (default to internal service)
PG_HOST = os.environ.get("PG_HOST", "postgresql-service")   # PostgreSQL service host
PG_USER = os.environ.get("PG_USER", "user")                 # PostgreSQL user (replace with your actual user or secret)
PG_PASSWORD = os.environ.get("PG_PASSWORD", "password")     # PostgreSQL password (use environment variables or Kubernetes Secrets)
PG_DB = os.environ.get("PG_DB", "ollama")                   # PostgreSQL database name

# Connect to Redis (using default Redis port 6379)
redis_client = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASSWORD,
    host=PG_HOST,
    port="5432"  # Default PostgreSQL port
)
cursor = conn.cursor()

@app.route('/')
def home():
    """Health check route to ensure the service is running."""
    return "Postprocess Service is running!"

@app.route('/postprocess', methods=['POST'])
def postprocess():
    """
    Endpoint to handle postprocessing requests.
    Caches the result in Redis and stores it in PostgreSQL.
    """
    data = request.get_json()
    
    # Cache result in Redis with a 1-hour expiration
    request_id = data.get("request_id", "default")  # Fallback to "default" if request_id is not provided
    redis_client.setex(request_id, 3600, str(data))  # Cache for 1 hour (3600 seconds)
    
    # Insert result into PostgreSQL for long-term storage
    insert_into_postgresql(request_id, data)
    
    return jsonify({"message": "Data cached and stored successfully"}), 200

def insert_into_postgresql(request_id, data):
    """
    Inserts the request_id and result data into the PostgreSQL database.
    """
    query = "INSERT INTO inference_results (request_id, result) VALUES (%s, %s)"
    cursor.execute(query, (request_id, str(data)))  # Store the request_id and result as a string
    conn.commit()  # Commit the transaction to ensure the data is saved

if __name__ == "__main__":
    # Run the Flask app in debug mode on all available IPs (host='0.0.0.0')
    # The port is configurable via the PORT environment variable, defaulting to 8080
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
