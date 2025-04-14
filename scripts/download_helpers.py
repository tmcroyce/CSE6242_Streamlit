"""
Helper functions for downloading large files from Google Drive
"""

import os
import gdown
import streamlit as st

# File IDs for Google Drive - you'll need to replace these with your actual file IDs
# after uploading the files to Google Drive
FILE_IDS = {
    'non_nest_PCA.pkl': 'YOUR_FILE_ID_HERE',
    'pitches_PCA.pkl': 'YOUR_FILE_ID_HERE',
    'relevant_artist_columns.pkl': 'YOUR_FILE_ID_HERE',
    'timbres_PCA.pkl': 'YOUR_FILE_ID_HERE'
}

def download_file_from_google_drive(file_name, output_path):
    """
    Download a file from Google Drive if it doesn't exist locally
    
    Parameters:
    file_name (str): Name of the file to download
    output_path (str): Full path where the file should be saved
    
    Returns:
    bool: True if file exists or was downloaded successfully, False otherwise
    """
    # Check if file already exists
    if os.path.exists(output_path):
        return True
    
    # Check if we have the file ID
    if file_name not in FILE_IDS:
        st.error(f"No Google Drive file ID found for {file_name}")
        return False
    
    file_id = FILE_IDS[file_name]
    
    # Check if file ID has been set
    if file_id == 'YOUR_FILE_ID_HERE':
        st.error(f"Please upload {file_name} to Google Drive and update the file ID in scripts/download_helpers.py")
        return False
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Show downloading message
        with st.spinner(f"Downloading {file_name} from Google Drive..."):
            # Download the file
            url = f'https://drive.google.com/uc?id={file_id}'
            gdown.download(url, output_path, quiet=False)
        
        # Verify file was downloaded
        if os.path.exists(output_path):
            st.success(f"Successfully downloaded {file_name}")
            return True
        else:
            st.error(f"Failed to download {file_name}")
            return False
    except Exception as e:
        st.error(f"Error downloading {file_name}: {str(e)}")
        return False

def ensure_data_files_exist(script_dir):
    """
    Ensure all required data files exist, downloading them from Google Drive if necessary
    
    Parameters:
    script_dir (str): Directory where the script is running
    
    Returns:
    bool: True if all files exist or were downloaded successfully, False otherwise
    """
    # List of required files
    required_files = [
        'non_nest_PCA.pkl',
        'pitches_PCA.pkl',
        'relevant_artist_columns.pkl',
        'timbres_PCA.pkl'
    ]
    
    all_files_exist = True
    
    for file_name in required_files:
        output_path = os.path.join(script_dir, 'data', file_name)
        file_exists = download_file_from_google_drive(file_name, output_path)
        all_files_exist = all_files_exist and file_exists
    
    return all_files_exist
