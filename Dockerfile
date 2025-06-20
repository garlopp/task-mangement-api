# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Don't store the package cache, keeping the image smaller
# --upgrade pip: Ensure we have the latest pip
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code to the working directory
COPY . .

# Expose the port the app runs on
# Render will automatically use this, but it's good practice
EXPOSE 8000

# Define the command to run your app
# Gunicorn is a production-grade WSGI server to run your FastAPI app.
# -w 4: Use 4 worker processes.
# -k uvicorn.workers.UvicornWorker: Use Uvicorn to run the workers.
# main:app: Look for an object named `app` in a file named `main.py`.
# --bind 0.0.0.0:$PORT: Bind to all network interfaces on the port specified by Render's $PORT env var.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
