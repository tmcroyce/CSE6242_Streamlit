#!/usr/bin/env python3
"""
Script to compress the large PKL files using different compression algorithms
This version tries multiple compression methods and keeps the best one
"""
import os
import sys
import pickle
import bz2
import gzip
import lzma
import time

def compress_pickle(pkl_file, methods=None):
    """
    Compress a pickle file using multiple methods and keep the best one
    
    Parameters:
    pkl_file (str): Path to the pickle file
    methods (list): List of compression methods to try, default is all available
    
    Returns:
    tuple: (best_method, best_path, original_size, compressed_size, ratio)
    """
    if methods is None:
        methods = ['gzip', 'bz2', 'lzma']
    
    print(f"Compressing {pkl_file}...")
    
    # Original file size in MB
    original_size = os.path.getsize(pkl_file) / (1024 * 1024)
    print(f"  Original size: {original_size:.2f} MB")
    
    # Load the pickle file
    try:
        start_time = time.time()
        with open(pkl_file, 'rb') as f:
            data = pickle.load(f)
        load_time = time.time() - start_time
        print(f"  Load time: {load_time:.2f} seconds")
    except Exception as e:
        print(f"  Error loading {pkl_file}: {str(e)}")
        return None, None, None, None, None
    
    results = []
    
    # Try each compression method
    for method in methods:
        output_file = f"{os.path.splitext(pkl_file)[0]}.{method}"
        
        try:
            start_time = time.time()
            
            if method == 'gzip':
                with gzip.open(output_file, 'wb', compresslevel=9) as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            elif method == 'bz2':
                with bz2.BZ2File(output_file, 'wb', compresslevel=9) as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            elif method == 'lzma':
                with lzma.open(output_file, 'wb', preset=9) as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            compress_time = time.time() - start_time
            
            # Get compressed file size
            compressed_size = os.path.getsize(output_file) / (1024 * 1024)
            ratio = original_size / compressed_size
            
            print(f"  {method.upper()} - Size: {compressed_size:.2f} MB, Ratio: {ratio:.2f}x, Time: {compress_time:.2f}s")
            
            # Verify we can load the compressed file
            start_time = time.time()
            if method == 'gzip':
                with gzip.open(output_file, 'rb') as f:
                    test_data = pickle.load(f)
            elif method == 'bz2':
                with bz2.BZ2File(output_file, 'rb') as f:
                    test_data = pickle.load(f)
            elif method == 'lzma':
                with lzma.open(output_file, 'rb') as f:
                    test_data = pickle.load(f)
            
            decompress_time = time.time() - start_time
            print(f"    Decompression time: {decompress_time:.2f}s")
            
            results.append({
                'method': method,
                'path': output_file,
                'size': compressed_size,
                'ratio': ratio,
                'compress_time': compress_time,
                'decompress_time': decompress_time
            })
        
        except Exception as e:
            print(f"  Error with {method}: {str(e)}")
    
    if not results:
        return None, None, None, None, None
    
    # Find the best compression (highest ratio)
    best = max(results, key=lambda x: x['ratio'])
    
    print(f"\n  Best compression: {best['method'].upper()} - {best['size']:.2f} MB ({best['ratio']:.2f}x smaller)")
    
    # Remove other files
    for result in results:
        if result['path'] != best['path'] and os.path.exists(result['path']):
            os.remove(result['path'])
    
    return best['method'], best['path'], original_size, best['size'], best['ratio']

def update_code_instructions(results):
    """Generate instructions for updating code to use compressed files"""
    if not results:
        return
    
    print("\nTo use these compressed files in your code, add the following helper function:\n")
    print("```python")
    print("import pickle")
    print("import bz2")
    print("import gzip")
    print("import lzma")
    print("")
    print("def load_compressed_pickle(file_path):")
    print("    \"\"\"Load a compressed pickle file\"\"\"")
    print("    if file_path.endswith('.gzip'):")
    print("        with gzip.open(file_path, 'rb') as f:")
    print("            return pickle.load(f)")
    print("    elif file_path.endswith('.bz2'):")
    print("        with bz2.BZ2File(file_path, 'rb') as f:")
    print("            return pickle.load(f)")
    print("    elif file_path.endswith('.lzma'):")
    print("        with lzma.open(file_path, 'rb') as f:")
    print("            return pickle.load(f)")
    print("    else:")
    print("        with open(file_path, 'rb') as f:")
    print("            return pickle.load(f)")
    print("```\n")
    
    print("Then replace your current loading code with:\n")
    
    for result in results:
        if result['success']:
            orig_file = result['file']
            new_file = result['output']
            print(f"# Instead of: with open('{orig_file}', 'rb') as f:")
            print(f"#               data = pickle.load(f)")
            print(f"data = load_compressed_pickle('{new_file}')")
            print("")

def main():
    # Define the PKL files to compress
    pkl_files = [
        'data/non_nest_PCA.pkl',
        'data/pitches_PCA.pkl',
        'data/relevant_artist_columns.pkl',
        'data/timbres_PCA.pkl'
    ]
    
    results = []
    
    # Compress each PKL file
    for pkl_file in pkl_files:
        # Check if the PKL file exists
        if not os.path.exists(pkl_file):
            print(f"Error: {pkl_file} does not exist.")
            continue
        
        # Compress the file
        method, output_path, orig_size, comp_size, ratio = compress_pickle(pkl_file)
        
        results.append({
            'file': pkl_file,
            'success': method is not None,
            'method': method,
            'output': output_path,
            'orig_size': orig_size,
            'comp_size': comp_size,
            'ratio': ratio
        })
    
    # Print summary
    print("\nCompression Summary:")
    print("-------------------")
    for result in results:
        if result['success']:
            print(f"{result['file']} → {result['output']}")
            print(f"  {result['orig_size']:.2f} MB → {result['comp_size']:.2f} MB ({result['ratio']:.2f}x smaller)")
        else:
            print(f"{result['file']} - FAILED")
    
    # Print instructions for using compressed files
    update_code_instructions(results)

if __name__ == "__main__":
    main()
