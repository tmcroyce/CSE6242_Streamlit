#!/usr/bin/env python3
"""
Script to download required data files for the Music Similarity Visualization app
"""
import os
import sys
import streamlit as st
from scripts.download_helpers import ensure_data_files_exist

def main():
    print("Downloading required data files for Music Similarity Visualization app...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure all required data files exist
    data_files_exist = ensure_data_files_exist(script_dir)
    
    if data_files_exist:
        print("All data files successfully downloaded!")
        return 0
    else:
        print("Error: Failed to download some data files. See error messages above.")
        print("Please upload the missing files to Google Drive and update the file IDs in scripts/download_helpers.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
