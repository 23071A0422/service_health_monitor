# Use a lightweight Python image for smaller attack surface (InfoSec best practice)
FROM python:3.10-slim

# Set the working directory
WORKDIR /opt/sre_monitor

# Copy only requirements first to cache the pip install step
COPY requirements.txt .

# Install dependencies without cache to keep image size small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure the logs directory exists with correct permissions
RUN mkdir -p logs && chmod 777 logs

# Run the daemon
CMD ["python", "monitor/main.py"]