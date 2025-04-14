#!/usr/bin/env python3
"""
Improved script to convert the large PKL files to smaller formats
with better handling of sparse matrices and multi-dimensional arrays
"""
import os
import sys
import pandas as pd
import pickle
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from scipy import sparse
import h5py

def convert_pickle_to_efficient_format(pkl_file, output_file=None):
    """
    Convert a pickle file to a more efficient format based on content type
    
    Parameters:
    pkl_file (str): Path to the pickle file
    output_file (str): Optional output path, if None uses the same name with new extension
    
    Returns:
    tuple: (success, output_path, format_used)
    """
    if output_file is None:
        # Default to same filename with .h5 extension
        output_file = os.path.splitext(pkl_file)[0] + ".h5"
    
    print(f"Converting {pkl_file}...")
    
    try:
        # Load the pickle file
        with open(pkl_file, 'rb') as f:
            data = pickle.load(f)
        
        # Determine the data type and choose appropriate format
        if isinstance(data, pd.DataFrame):
            # Handle DataFrame
            if data.columns.nlevels > 1:
                # Convert multi-level columns to string
                data.columns = [str(col) for col in data.columns]
            
            # Check for sparse data
            has_sparse = False
            for col in data.columns:
                if pd.api.types.is_sparse(data[col].dtype):
                    has_sparse = True
                    # Convert sparse to dense for compatibility
                    data[col] = data[col].sparse.to_dense()
            
            # Use HDF5 for DataFrames
            output_file = os.path.splitext(pkl_file)[0] + ".h5"
            data.to_hdf(output_file, key='data', mode='w')
            format_used = "HDF5"
            
        elif isinstance(data, np.ndarray):
            # For numpy arrays, use HDF5
            output_file = os.path.splitext(pkl_file)[0] + ".h5"
            with h5py.File(output_file, 'w') as f:
                f.create_dataset('data', data=data, compression='gzip', compression_opts=9)
            format_used = "HDF5"
            
        elif isinstance(data, sparse.spmatrix):
            # For sparse matrices, use npz format
            output_file = os.path.splitext(pkl_file)[0] + ".npz"
            sparse.save_npz(output_file, data, compressed=True)
            format_used = "NPZ (Sparse)"
            
        elif isinstance(data, dict):
            # For dictionaries, try HDF5
            output_file = os.path.splitext(pkl_file)[0] + ".h5"
            with h5py.File(output_file, 'w') as f:
                # Handle different types in the dictionary
                for key, value in data.items():
                    if isinstance(value, np.ndarray):
                        f.create_dataset(str(key), data=value, compression='gzip', compression_opts=9)
                    else:
                        # Convert to string or numpy array
                        try:
                            f.create_dataset(str(key), data=np.array([str(value)]), compression='gzip')
                        except:
                            print(f"  Warning: Could not save key {key} with value type {type(value)}")
            format_used = "HDF5"
            
        else:
            # For other types, fallback to pickle with improved compression
            import bz2
            output_file = os.path.splitext(pkl_file)[0] + ".pbz2"
            with bz2.BZ2File(output_file, 'wb', compresslevel=9) as f:
                pickle.dump(data, f)
            format_used = "Compressed Pickle (BZ2)"
        
        # Print size comparison
        pkl_size = os.path.getsize(pkl_file) / (1024 * 1024)  # MB
        new_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"  Original size: {pkl_size:.2f} MB")
        print(f"  New size ({format_used}): {new_size:.2f} MB")
        print(f"  Compression ratio: {pkl_size/new_size:.2f}x")
        
        return True, output_file, format_used
    
    except Exception as e:
        print(f"  Error converting {pkl_file}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None, None

def main():
    # Define the PKL files to convert
    pkl_files = [
        'data/non_nest_PCA.pkl',
        'data/pitches_PCA.pkl',
        'data/relevant_artist_columns.pkl',
        'data/timbres_PCA.pkl'
    ]
    
    results = []
    
    # Convert each PKL file
    for pkl_file in pkl_files:
        # Check if the PKL file exists
        if not os.path.exists(pkl_file):
            print(f"Error: {pkl_file} does not exist.")
            continue
        
        # Convert the file
        success, output_path, format_used = convert_pickle_to_efficient_format(pkl_file)
        
        results.append({
            'file': pkl_file,
            'success': success,
            'output': output_path,
            'format': format_used
        })
    
    # Print summary
    print("\nConversion Summary:")
    print("------------------")
    for result in results:
        status = "SUCCESS" if result['success'] else "FAILED"
        if result['success']:
            print(f"{result['file']} → {result['output']} ({result['format']}) - {status}")
        else:
            print(f"{result['file']} - {status}")
    
    print("\nRemember to update your code to use these new file formats.")

if __name__ == "__main__":
    main()
