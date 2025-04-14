"""
Utility functions for file operations, especially for loading compressed data files
"""
import os
import pickle
import bz2
import gzip
import lzma

def load_compressed_pickle(file_path):
    """
    Load a compressed pickle file in various formats
    
    Parameters:
    file_path (str): Path to the compressed pickle file
    
    Returns:
    object: The loaded pickle object
    """
    # For normal or compressed pickle files
    if file_path.endswith('.gzip'):
        with gzip.open(file_path, 'rb') as f:
            return pickle.load(f)
    elif file_path.endswith('.bz2'):
        with bz2.BZ2File(file_path, 'rb') as f:
            return pickle.load(f)
    elif file_path.endswith('.lzma'):
        with lzma.open(file_path, 'rb') as f:
            return pickle.load(f)
    else:
        # Regular pickle file
        with open(file_path, 'rb') as f:
            return pickle.load(f)
