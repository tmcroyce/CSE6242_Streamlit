#!/bin/bash

# Make script executable
chmod +x setup.sh

# Ensure pip is up to date
pip install --upgrade pip

# Install system dependencies needed for Pillow and other packages
if command -v apt-get &> /dev/null; then
    # For Debian/Ubuntu
    apt-get update
    apt-get install -y --no-install-recommends zlib1g-dev libjpeg-dev libpng-dev
fi

# Install Python dependencies - use wheels where possible
pip install --prefer-binary -r requirements.txt

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
