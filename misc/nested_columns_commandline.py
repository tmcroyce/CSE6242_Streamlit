import pandas as pd
import re
import time
import numpy as np
import ast
import sys




def nested_column_to_dict(df, inlist): 
    start = time.time()
    outdict = dict()
    for col in inlist: 
        print("Okay, we're starting in on column " + col)
        coltime = time.time()
        nested_list_column = df[col].apply(lambda x: ast.literal_eval(x))
        print(f"First bit took {time.time()-coltime} seconds")
        nested_list_outer_len = nested_list_column.apply(lambda x: len(x)).max()
        print(f"Outer bit took {time.time()-coltime} seconds")
        nested_list_inner_len = nested_list_column.apply(lambda x: max([len(i) for i in x])).max()
        lentime = time.time()
        print(f"Getting lengths took {lentime - coltime} seconds. {lentime - start} seconds have passed in total.")
        for outer in range(nested_list_outer_len):
            for inner in range(nested_list_inner_len): 
                outdict[f"{col}_{outer}_{inner}"] = [None for _ in range(df.shape[0])]
        skeletontime = time.time()
        print(f"Setting up the Nones took {skeletontime - lentime} seconds. This column has taken {skeletontime-coltime} seconds. {skeletontime - start} seconds have passed in total")
        for row in range(df.shape[0]): 
            for outer_dex in range(len(nested_list_column.iloc[row])): 
                for inner_dex in range(len(nested_list_column.iloc[row][outer_dex])): 
                    outdict[f"{col}_{outer_dex}_{inner_dex}"][row] = nested_list_column.iloc[row][outer_dex][inner_dex]
            if row % 500 == 0:
                print(f"I am on row {row} out of {df.shape[0]}")
        colendtime = time.time()
        print(f"Doing this column took {colendtime - coltime} seconds. {colendtime-start} seconds have passed in total")
    return outdict

def drop_na_cols(df, threshold = 0.95): 
    df_isnan_sum = df.isna().sum()
    df_isnan_bool = (df_isnan_sum <= df.shape[0] * threshold) == True
    df_isnan_bool = df_isnan_bool[df_isnan_bool].index
    df = df[df_isnan_bool]
    return df


filename = "../EDA/millionsong_subset.csv"
subset = pd.read_csv(filename)

use_columns = ['artist_familiarity','artist_hotttnesss','song_hotttnesss', 'key','loudness', 'tempo', 'time_signature','year','artist_location']
use_columns += ['similar_artists','artist_terms','artist_mbtags'] 

use_subset = subset[use_columns]

use_non_nest_list_cols = ['segments_start','segments_loudness_max','segments_loudness_max_time',
                          'segments_loudness_start','sections_start','beats_start','bars_start','tatums_start']
non_nest_list_subset = subset[use_non_nest_list_cols]

possible_nest_list_cols = ['segments_pitches','segments_timbre']
nest_list_subset = subset[possible_nest_list_cols]

expanded_nested_pitches = nested_column_to_dict(nest_list_subset.iloc[0:10000], [list(nest_list_subset.columns)[1]])
enp_keys = list(expanded_nested_pitches.keys())
enp_keys_len = len(enp_keys)


expanded_nested_pitches = {i:expanded_nested_pitches[i] for i in enp_keys[0:enp_keys_len//3]}

check_something = time.time()

exp_nest_pitch_df = pd.DataFrame(expanded_nested_pitches)

df_time = time.time()

print(f"Okay, converting to a dataframe took {df_time - check_something}")

test_df_size =  sys.getsizeof(exp_nest_pitch_df)

print(f"This file is {test_df_size/(1024 ** 2)} megabytes")
print(f"Let's clear some of this out. ")

clear_df = drop_na_cols(exp_nest_pitch_df)
clear_df_size = sys.getsizeof(clear_df)

print(f"Now this file is {clear_df_size/(1024 ** 2)} megabytes")

last_start_time = time.time()

clear_df.to_csv("segments_timbre_unpacked_95_percent_nonnan.csv")

print(time.time()-last_start_time)