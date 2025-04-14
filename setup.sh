#!/bin/bash

# Make script executable
chmod +x setup.sh

# Print debug information
echo "Starting setup.sh script"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"

# Ensure pip is up to date
pip install --upgrade pip

# Verify system packages (will be installed via packages.txt on Streamlit Cloud)
echo "Installed system packages:"
if command -v apt-get &> /dev/null; then
    apt list --installed | grep -E 'zlib|jpeg|png|lzma|dev'
fi

# Clean any previous installations of critical packages
echo "Cleaning previous installations of critical packages"
pip uninstall -y pandas numpy scikit-learn

# Install critical dependencies first with exact versions and binary preference
echo "Installing critical dependencies"
pip install --prefer-binary pandas==2.0.3 numpy==1.24.3 scikit-learn==1.3.0

# Install remaining Python dependencies from requirements.txt
echo "Installing remaining dependencies from requirements.txt"
pip install --prefer-binary -r requirements.txt

# List all installed packages for debugging
echo "All installed packages:"
pip list

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

echo "Setup complete"
