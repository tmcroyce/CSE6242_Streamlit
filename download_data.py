#!/usr/bin/env python3
"""
Script to download required data files for the Music Similarity Visualization app
"""
import os
import sys
import requests
import streamlit as st
from scripts.download_helpers import extract_zip, setup_directories, ensure_data_files_exist

def main():
    print("Downloading required data files for Music Similarity Visualization app...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # SharePoint link to the data file
    sharepoint_url = "https://gtvault-my.sharepoint.com/personal/sstewart78_gatech_edu/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fsstewart78%5Fgatech%5Fedu%2FDocuments%2Frestructured%20files%20and%20script%20for%20similarity%20analysis%2Ezip&parent=%2Fpersonal%2Fsstewart78%5Fgatech%5Fedu%2FDocuments&ga=1"
    output = "data/archive.zip"
    
    # Create directories if they don't exist
    setup_directories()
    
    # Download the zip file
    if not os.path.exists(output):
        print("Downloading archive.zip from SharePoint...")
        print("NOTE: The provided SharePoint link requires authentication and direct download may not be possible.")
        print("Please download the file manually from:")
        print(sharepoint_url)
        print(f"And place it in the '{output}' path.")
        
        # We can't directly download from SharePoint without authentication
        # Wait for user confirmation that they've manually downloaded the file
        while not os.path.exists(output):
            user_input = input("Have you downloaded and placed the file in the correct location? (yes/no): ")
            if user_input.lower() == "yes":
                if os.path.exists(output):
                    print("File detected. Proceeding with extraction.")
                    break
                else:
                    print(f"File not found at '{output}'. Please check the location.")
            else:
                print("Please download the file to continue.")
    else:
        print("archive.zip already exists, skipping download.")
    
    # Extract the zip file if it exists
    if os.path.exists(output):
        extract_zip(output, "data/")
        
        # Ensure all required data files exist
        data_files_exist = ensure_data_files_exist(script_dir)
        
        if data_files_exist:
            print("All data files successfully downloaded!")
            return 0
        else:
            print("Error: Failed to download some data files. See error messages above.")
            print("Please upload the missing files to SharePoint and update the file IDs in scripts/download_helpers.py")
            return 1
    else:
        print("Data file not found. Setup incomplete.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
