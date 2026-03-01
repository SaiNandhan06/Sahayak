# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

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

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    OLLAMA_MODELS=/home/user/.ollama/models

# Create app directory and give ownership to user
RUN mkdir -p /app && chown -R user:user /app /home/user

# Switch to the "user" user
USER user

# Set working directory
WORKDIR /app

# Copy the entire backend
COPY --chown=user . .

# Install Python backend dependencies
ENV PATH="/home/user/.local/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Start Ollama, pull models, AND run data generation to build ChromaDB
RUN nohup bash -c "ollama serve &" && sleep 5 && \
    ollama pull qwen2:0.5b && \
    ollama pull nomic-embed-text && \
    python data_generation.py

# --- Setup Frontend ---
WORKDIR /app/Frontend
RUN npm install --legacy-peer-deps
RUN npm run build

# Go back to the root directory
WORKDIR /app

# Expose the Hugging Face required port
EXPOSE 7860

# Create a startup script
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'ollama serve &' >> /app/start.sh && \
    echo 'sleep 5' >> /app/start.sh && \
    echo 'uvicorn main:app --host 0.0.0.0 --port 7860' >> /app/start.sh

RUN chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]
