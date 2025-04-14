#!/bin/bash

# Make script executable
chmod +x setup.sh

# Ensure pip is up to date
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories if they don't exist
mkdir -p ~/.streamlit

# Create Streamlit config
cat > ~/.streamlit/config.toml << EOF
[server]
headless = true
enableCORS = false
EOF

# Create credentials file
cat > ~/.streamlit/credentials.toml << EOF
[general]
email = ""
EOF
