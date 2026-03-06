# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy your requirements and install them
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code
COPY . .

# Run the app using gunicorn (Production server)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app