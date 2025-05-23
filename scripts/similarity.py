#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 09:33:03 2025

@author: samue
"""

import pandas as pd
import re
import time
import numpy as np
import ast
import sys
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import pickle
import os
import lzma

# Import our custom download helper and file utility modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.download_helpers import ensure_data_files_exist
from scripts.file_utils import load_compressed_pickle

#Gets the cosine similarity between our given song vector and
#the other rows in the reference

def get_cossim(d, reference, index): 
    if type(d[index])==pd.Series:
        d_index = d[:,index].to_numpy().reshape(-1,1)
    else: 
        d_index = d[index]
    a = d_index.reshape(1, -1)  # Query vector
    similarities = cosine_similarity(a, d)[0]  # Compute similarity for all rows
    outlist = sorted(enumerate(similarities), key=lambda x: -x[1]) 
    return outlist

# Runs through original data set and prints out artist names and artist terms. 
# Mostly for checking if the rest of this is working well.

# get_terms is only if you want to see the artist_terms. I don't recommend it,
# because it's gonna clutter up the output. I just had it on hand because it
# was useful when checing accuracy. 

def check_artists(inlist, reference,listlen=10):
    #get_terms = lambda x: ast.literal_eval(reference.iloc[inlist[x][0]]['artist_terms'])[0:5]
    a = [[inlist[i][0],
          reference.iloc[inlist[i][0]]['artist_name'], 
          reference.iloc[inlist[i][0]]['title'],  
          reference.iloc[inlist[i][0]]['year'],
          inlist[i][1]  
         ] for i in range(listlen)]
    b = '\n'.join([str(i) for i in a])
    return a, b


# Combines and and weights the measurements from earlier
def combine_cos_sims(inlist, weights = None):
    if weights == None: 
        weights = [1/sum(weights) for _ in inlist]
    #This else clause was just for normalizing the weights. Didn't seem super useful, though.
    else: 
        weights = [i/sum(weights) for i in weights]
    inlist = [sorted(i, key = lambda x: x[0]) for i in inlist]
    inlist = [[inlist[0][i][0], sum([(inlist[j][i][1]*weights[j]) for j in range(len(inlist))])] for i in range(len(inlist[0]))]
    return sorted(inlist, key = lambda x: -x[1])


def similar_artists_id_and_cossim(df, index): 
    row = df.iloc[index]
    sorted_row = row[2:len(row)].sort_values(ascending=False)
    outlist = [(sorted_row.index[i], sorted_row.iloc[i]) for i in range(len(sorted_row))]
    return outlist

def reorder(in_array,ref):
    label_to_index = {str(label): i for i, label in enumerate(in_array['label'])}
    #print(label_to_index.keys())
    indices = [label_to_index[label] for label in ref]
    ordered_data = in_array['data'][indices]
    return ordered_data

if __name__ == '__main__':
    # Use absolute paths relative to the script location
    import os
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure all required data files exist
    data_files_exist = ensure_data_files_exist(script_dir)
    if not data_files_exist:
        print("Error: Missing required data files. Please make sure all data files are available.")
        sys.exit(1)
    
    # Now load the data files
    genre_PCA = pd.read_csv(os.path.join(script_dir, 'data/artist_term_components.csv'), index_col='Unnamed: 0')
    
    # Load compressed pickle files using the helper function
    similar_artists = load_compressed_pickle(os.path.join(script_dir, 'data/relevant_artist_columns.lzma'))
    pitches_PCA = load_compressed_pickle(os.path.join(script_dir, 'data/pitches_PCA.lzma'))
    timbre_PCA = load_compressed_pickle(os.path.join(script_dir, 'data/timbres_PCA.lzma'))
    non_nest_PCA = load_compressed_pickle(os.path.join(script_dir, 'data/non_nest_PCA.lzma'))
    
    subset = pd.read_csv(os.path.join(script_dir, 'data/artist_id_and_name.csv'), index_col='song_id')
    
    label_order = list(subset.index)
    
    pitches_PCA = reorder(pitches_PCA,label_order)
    timbre_PCA = reorder(timbre_PCA,label_order)
    non_nest_PCA = reorder(non_nest_PCA,label_order)


    # Processes command-line arguments
    
    if len(sys.argv) > 3: 
        artist_output = int(sys.argv[3])+1
    else: 
        artist_output = 11
    if len(sys.argv) > 2: 
        weights = sys.argv[2][1:-1]
        weights = list(weights.split(','))
        weights = [float(i) for i in weights]
    else: 
        weights = [1 for _ in range(4)] + [2]
    if len(sys.argv) > 1: 
        compare_row_id = sys.argv[1]
    else: 
        compare_row_id = "SOCWJDB12A58A776AF"


    compare_row = subset.index.get_loc(compare_row_id)
    
    non_nest_PCA_checklist = get_cossim(non_nest_PCA, subset, compare_row)
    pitches_PCA_checklist  = get_cossim(pitches_PCA,subset,compare_row)
    timbre_PCA_checklist = get_cossim(timbre_PCA,subset,compare_row)
    genre_PCA_checklist = get_cossim(genre_PCA.to_numpy(),subset,compare_row)
    similar_artists_checklist = similar_artists_id_and_cossim(similar_artists,compare_row)
    
    
    
    use_list = [non_nest_PCA_checklist,pitches_PCA_checklist,timbre_PCA_checklist,
                genre_PCA_checklist,similar_artists_checklist]
    cossim_combined = combine_cos_sims(use_list,weights)
    outlist, outstr = check_artists(cossim_combined,subset,artist_output)
    outlist = np.array([np.array(i) for i in outlist])
    outlist = pd.DataFrame(outlist)
    outlist = outlist.iloc[1:] # Skip the first row which is the center node itself
    
    # Ensure we're setting the correct column names
    outlist = outlist.set_axis(['index','artist_name','song_title','year','weighted_similarity'],axis=1)
    
    # Reset index and add rank column
    outlist = outlist.reset_index().rename(columns={"level_0": "rank"})
    
    # Debug output to help troubleshoot
    print(outlist.to_csv(index=False), end="")
