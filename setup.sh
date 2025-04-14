#!/bin/bash

# Make script executable
chmod +x setup.sh

# Ensure pip is up to date
pip install --upgrade pip

# Install system dependencies needed for Pillow and other packages
if command -v apt-get &> /dev/null; then
    # For Debian/Ubuntu
    apt-get update
    apt-get install -y --no-install-recommends zlib1g-dev libjpeg-dev libpng-dev liblzma-dev
fi

# Force a clean reinstall of critical packages to ensure they're properly installed
pip uninstall -y pandas numpy scikit-learn
pip install --prefer-binary pandas>=2.1.0 numpy>=1.26.0 scikit-learn>=1.3.0

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
