#!/bin/bash

# Make script executable
chmod +x setup.sh

# Print debug information
echo "Starting setup.sh script"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"

# Ensure pip is up to date
pip install --upgrade pip

# Install setuptools and wheel first to handle missing distutils in Python 3.12+
pip install setuptools==69.0.2 wheel==0.42.0

# Verify system packages (will be installed via packages.txt on Streamlit Cloud)
echo "Installed system packages:"
if command -v apt-get &> /dev/null; then
    apt list --installed | grep -E 'zlib|jpeg|png|lzma|dev'
fi

# Clean any previous installations of critical packages
echo "Cleaning previous installations of critical packages"
pip uninstall -y pandas numpy scikit-learn setuptools wheel

# Install critical dependencies first with binary preference
echo "Installing critical dependencies"
pip install --prefer-binary setuptools==69.0.2 wheel==0.42.0
pip install --prefer-binary numpy==1.26.3

# Install remaining Python dependencies from requirements.txt
echo "Installing remaining dependencies from requirements.txt"
pip install --prefer-binary -r requirements.txt

# Verify the key packages installed successfully
echo "Verifying pandas installation:"
python -c "import pandas; print(f'pandas version: {pandas.__version__}')" || echo "Failed to import pandas"

echo "Verifying numpy installation:"
python -c "import numpy; print(f'numpy version: {numpy.__version__}')" || echo "Failed to import numpy"

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
