#!/usr/bin/env python3
"""
Script to convert the large PKL files to Parquet format for better compression and performance
"""
import os
import sys
import pandas as pd
import pickle
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

def convert_pickle_to_parquet(pkl_file, parquet_file):
    """
    Convert a pickle file to parquet format
    
    Parameters:
    pkl_file (str): Path to the pickle file
    parquet_file (str): Path where the parquet file should be saved
    
    Returns:
    bool: True if conversion was successful, False otherwise
    """
    print(f"Converting {pkl_file} to {parquet_file}...")
    
    try:
        # Load the pickle file
        with open(pkl_file, 'rb') as f:
            data = pickle.load(f)
        
        # Handle different data types
        if isinstance(data, pd.DataFrame):
            # If it's already a DataFrame, we can directly save as parquet
            data.to_parquet(parquet_file, index=True)
        elif isinstance(data, dict):
            # If it's a dictionary, convert to DataFrame first
            df = pd.DataFrame.from_dict(data, orient='index')
            df.to_parquet(parquet_file, index=True)
        elif isinstance(data, np.ndarray):
            # If it's a numpy array, convert to DataFrame
            if data.ndim == 1:
                df = pd.DataFrame(data.reshape(-1, 1))
            else:
                df = pd.DataFrame(data)
            df.to_parquet(parquet_file, index=True)
        else:
            # For other types, try to convert to DataFrame or use pyarrow directly
            print(f"Attempting to handle data of type: {type(data)}")
            
            # Try to convert to dict first, then DataFrame
            try:
                data_dict = {}
                for i, item in enumerate(data):
                    data_dict[i] = item
                df = pd.DataFrame.from_dict(data_dict, orient='index')
                df.to_parquet(parquet_file, index=True)
            except Exception as e:
                print(f"Could not convert to dict: {str(e)}")
                
                # Try direct serialization with pyarrow
                try:
                    # Serialize data to pyarrow Table
                    table = pa.Table.from_pydict({"data": [pickle.dumps(data)]})
                    pq.write_table(table, parquet_file)
                except Exception as inner_e:
                    print(f"Error serializing with pyarrow: {str(inner_e)}")
                    return False
        
        print(f"Successfully converted {pkl_file} to {parquet_file}")
        
        # Print size comparison
        pkl_size = os.path.getsize(pkl_file) / (1024 * 1024)  # MB
        parquet_size = os.path.getsize(parquet_file) / (1024 * 1024)  # MB
        print(f"Original PKL size: {pkl_size:.2f} MB")
        print(f"Parquet size: {parquet_size:.2f} MB")
        print(f"Compression ratio: {pkl_size/parquet_size:.2f}x")
        
        return True
    
    except Exception as e:
        print(f"Error converting {pkl_file} to parquet: {str(e)}")
        return False

def main():
    # Define the PKL files to convert
    pkl_files = [
        'data/non_nest_PCA.pkl',
        'data/pitches_PCA.pkl',
        'data/relevant_artist_columns.pkl',
        'data/timbres_PCA.pkl'
    ]
    
    # Convert each PKL file to Parquet
    for pkl_file in pkl_files:
        # Define the output Parquet file path
        parquet_file = pkl_file.replace('.pkl', '.parquet')
        
        # Check if the PKL file exists
        if not os.path.exists(pkl_file):
            print(f"Error: {pkl_file} does not exist.")
            continue
        
        # Convert the file
        success = convert_pickle_to_parquet(pkl_file, parquet_file)
        
        if not success:
            print(f"Failed to convert {pkl_file}")
    
    print("Conversion complete.")

if __name__ == "__main__":
    main()
