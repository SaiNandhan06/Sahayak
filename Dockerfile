FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy the entire backend
COPY . .

# Install Python backend dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- Setup Frontend ---
# Make sure we're in the frontend dir, install deps, and build
WORKDIR /app/Frontend
RUN npm install --legacy-peer-deps
RUN npm run build

# Go back to the root directory
WORKDIR /app

# Expose the FastAPI port
EXPOSE 8000

# Create a startup script
RUN echo '#!/bin/bash\n\
# Start Ollama service in the background\n\
ollama serve &\n\
sleep 5\n\
# Pull the required models (if not already cached)\n\
ollama pull qwen2:0.5b\n\
ollama pull nomic-embed-text\n\
# Set the FastAPI to serve the built frontend statically\n\
# Start FastAPI\n\
uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]
