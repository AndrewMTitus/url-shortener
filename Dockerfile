# Use the official Python image
FROM python:3.9

# Create and change to the app directory
WORKDIR /usr/src/app

# Copy application dependency manifests to the container image.
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY . .

# Run the web service on container startup.
CMD ["python", "./main.py"]

# Document that the service listens on port 8000.
EXPOSE 8000

