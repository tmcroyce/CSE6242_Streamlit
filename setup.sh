#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories if they don't exist
mkdir -p ~/.streamlit

# Create Streamlit config
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml

echo "[theme]
primaryColor = '#FF4B4B'
backgroundColor = '#FFFFFF'
secondaryBackgroundColor = '#F0F2F6'
textColor = '#262730'
font = 'sans serif'
" > ~/.streamlit/config.toml
