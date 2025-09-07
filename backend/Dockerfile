# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which reduces the image size.
# --trusted-host pypi.python.org: Can help in environments with proxy issues.
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the backend application code into the container at /app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables (can be overridden at runtime)
# Set a default URL for Ollama, which assumes it's running on the host machine
# When deploying to Kubernetes, you'll need to point this to the correct service address.
ENV OLLAMA_BASE_URL="http://192.168.1.15:11434"
ENV OLLAMA_MODEL="llama3:latest"

# Run app.py when the container launches
# Use gunicorn in production for better performance
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
# For simplicity in this example, we'll use the Flask development server.
CMD ["python", "app.py"]
