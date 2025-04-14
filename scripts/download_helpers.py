"""
Helper functions for downloading large files from SharePoint
"""

import os
import zipfile
import streamlit as st
import requests
from urllib.parse import urlparse
import base64

# SharePoint link to the data folder
SHAREPOINT_URL = "https://gtvault-my.sharepoint.com/personal/sstewart78_gatech_edu/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fsstewart78%5Fgatech%5Fedu%2FDocuments%2Frestructured%20files%20and%20script%20for%20similarity%20analysis%2Ezip&parent=%2Fpersonal%2Fsstewart78%5Fgatech%5Fedu%2FDocuments&ga=1"

# Required data files that should be extracted from the archive
REQUIRED_FILES = [
    'non_nest_PCA.pkl',
    'pitches_PCA.pkl',
    'relevant_artist_columns.pkl',
    'timbres_PCA.pkl'
]

def setup_directories():
    """
    Create necessary directories for the app if they don't exist.
    """
    directories = ["data", "temp"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def extract_zip(zip_path, extract_to):
    """
    Extract a zip file to the specified directory.
    
    Parameters:
    zip_path (str): Path to the zip file
    extract_to (str): Directory to extract to
    """
    if not os.path.exists(zip_path):
        print(f"Error: {zip_path} does not exist.")
        return False
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            print(f"Extracting {zip_path} to {extract_to}...")
            zip_ref.extractall(extract_to)
            print("Extraction complete.")
            return True
    except Exception as e:
        print(f"Error extracting {zip_path}: {str(e)}")
        return False

def download_data_guide():
    """
    Display instructions for downloading data from SharePoint in the Streamlit app
    """
    st.markdown("## Data Files Required")
    st.markdown("""
    ### This application requires data files that aren't included in the repository.
    
    #### Option 1: Download from SharePoint (Georgia Tech Login Required)
    1. Click the link below to access the data files on SharePoint:
    """)
    
    st.markdown(f"[Download Data Files]({SHAREPOINT_URL})")
    
    st.markdown("""
    2. Download the ZIP file and extract the contents to your computer
    3. Upload each of the following required files using the file uploader below:
    """)
    
    for file in REQUIRED_FILES:
        st.markdown(f"- {file}")
    
    uploaded_files = {}
    
    # Create a file uploader for each required file
    st.markdown("### Upload Required Files")
    
    for file in REQUIRED_FILES:
        uploaded_file = st.file_uploader(f"Upload {file}", type=['pkl'])
        if uploaded_file is not None:
            # Save the uploaded file to the data directory
            save_uploaded_file(uploaded_file, os.path.join("data", file))
            uploaded_files[file] = True
    
    # Check if all files have been uploaded
    if len(uploaded_files) == len(REQUIRED_FILES):
        st.success(" All required files have been uploaded! You can now use the application.")
        st.session_state['data_files_uploaded'] = True
        # Add a button to refresh the page
        if st.button("Continue to the Application"):
            st.experimental_rerun()
        return True
    
    return False

def save_uploaded_file(uploaded_file, save_path):
    """
    Save an uploaded file to the specified path
    
    Parameters:
    uploaded_file: The uploaded file object from st.file_uploader
    save_path (str): Path where the file should be saved
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save the file
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return True

def ensure_data_files_exist(script_dir):
    """
    Ensure all required data files exist, guiding user to download from SharePoint if necessary
    
    Parameters:
    script_dir (str): Directory where the script is running
    
    Returns:
    bool: True if all files exist, False otherwise
    """
    # Check if we're already tracking that files were uploaded in this session
    if 'data_files_uploaded' in st.session_state and st.session_state['data_files_uploaded']:
        return True
    
    all_files_exist = True
    missing_files = []
    
    # Check if each required file exists
    for file_name in REQUIRED_FILES:
        file_path = os.path.join(script_dir, 'data', file_name)
        if not os.path.exists(file_path):
            missing_files.append(file_name)
            all_files_exist = False
    
    # If files are missing, provide a way to upload them
    if not all_files_exist:
        st.warning("Some required data files are missing:")
        for file in missing_files:
            st.warning(f"- {file}")
        
        # Show data download guide
        if download_data_guide():
            return True
        else:
            return False
    
    # All files exist
    st.session_state['data_files_uploaded'] = True
    return True
