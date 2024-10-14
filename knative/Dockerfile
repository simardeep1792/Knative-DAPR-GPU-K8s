# Use the official lightweight Python image
FROM python:3.7-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Set the working directory inside the container
ENV APP_HOME /app
WORKDIR $APP_HOME

# Create a non-root user with a specific numeric UID (e.g., 1337)
RUN addgroup --system mygroup && adduser --system --ingroup mygroup --uid 1337 myuser

# Copy the requirements.txt from the current service directory
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code (app.py) into the container
COPY app.py .

# Change ownership of the application code to the non-root user
RUN chown -R 1337:1337 /app

# Switch to the non-root user
USER 1337

# Expose the default port (8080)
EXPOSE 8080

# Run the web service on container startup using gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
