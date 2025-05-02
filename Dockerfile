# Use a slim Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose Streamlit’s default port
EXPOSE 8501

# Start Streamlit app
CMD ["streamlit", "run", "agent_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
