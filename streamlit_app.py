import streamlit as st
import subprocess
import os
import pandas as pd
import json
import csv
import sys
import io
import networkx as nx
from pyvis.network import Network
import tempfile
from pathlib import Path
import math


st.set_page_config(
    page_title="Music Similarity Visualization",
    page_icon="🎵",
    layout="wide"
)

st.title("Music Similarity Visualization")
st.markdown("Find similar songs based on various audio features.")

# Add How To Use This App expander
with st.expander("How To Use This App"):
    st.markdown("""
    ### Getting Started
    
    1. **Select a center song** that you want to base your recommendations on. You can do this by searching for a song or artist in the searchbar or selecting a song in the list (which currently has 'Rick Astley - Never Gonna Give You Up' in it).
    
    2. **Adjust the weights** you want to use for the similarity search. For example, if you want songs in a similar genre, increase the 'Genre Weight' and decrease the others.
    
    3. **Click 'Find Similar Songs'** to run the analysis.
    
    4. **Scroll down to "Watch Similar Songs on YouTube"** to watch the music videos of your selected songs (if available) or listen to them (if music videos are not available).
    """)

# Control Sidebar
with st.sidebar:
    st.header("Visualization Controls")
    
    # Weights 
    st.subheader("Feature Weights")
    
    default_weight1 = 1.0  # Loudness
    default_weight2 = 1.0  # Pitches
    default_weight3 = 1.0  # Timbre
    default_weight4 = 1.0  # Genre
    default_weight5 = 2.0  # Artist Similarity
    
    weight1 = st.slider("Loudness Weight", 0.0, 2.0, default_weight1, 0.1, 
                       help="Weight for loudness features")
    weight2 = st.slider("Pitches Weight", 0.0, 2.0, default_weight2, 0.1,
                       help="Weight for pitch features")
    weight3 = st.slider("Timbre Weight", 0.0, 2.0, default_weight3, 0.1,
                       help="Weight for timbre features")
    weight4 = st.slider("Genre Weight", 0.0, 2.0, default_weight4, 0.1,
                       help="Weight for genre features")
    weight5 = st.slider("Artist Similarity Weight", 0.0, 2.0, default_weight5, 0.1,
                       help="Weight for artist similarity")
    
    # Combine weights into a list after sliders are created
    weights = [weight1, weight2, weight3, weight4, weight5]
    
    # Year filter
    st.subheader("Year Filter")
    
    # Set default years
    years_range = st.slider("Filter by Year Range", 1900, 2025, (1900, 2025))
    include_unknown = st.checkbox("Include Unknown Years", value=True)

# Global constants
DEFAULT_CENTER_NODE = "SOCWJDB12A58A776AF"  # Rick Astley - Never Gonna Give You Up
DEFAULT_WEIGHTS = [1.0, 1.0, 1.0, 1.0, 2.0]

# load songs
@st.cache_data
def load_songs():
    songs = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'artist_id_and_name.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if row['song_id'] and row['artist_name'] and row['title']:
                    songs.append({
                        'id': row['song_id'],
                        'artist': row['artist_name'],
                        'title': row['title'],
                        'year': row['year'] if row['year'] and row['year'] != '0' else 'Unknown'
                    })
        
        # Add Rick Astley's "Never Gonna Give You Up" as first option if not already in list
        rick_astley_id = "SOCWJDB12A58A776AF"
        if not any(song['id'] == rick_astley_id for song in songs):
            songs.insert(0, {
                'id': rick_astley_id,
                'artist': 'Rick Astley',
                'title': 'Never Gonna Give You Up',
                'year': '1987'
            })
            
        return songs
    except Exception as e:
        st.error(f"Error loading songs: {str(e)}")
        return []

# filter songs by year and search term
def filter_songs(songs, search_term="", min_year=1900, max_year=2025, include_unknown=True):
    filtered_songs = []
    search_term = search_term.lower()
    
    for song in songs:
        year = song['year']
        if year == 'Unknown':
            if not include_unknown:
                continue
        else:
            try:
                year_int = int(year)
                if year_int < min_year or year_int > max_year:
                    continue
            except:
                if not include_unknown:
                    continue
        
        # search term filter
        if search_term:
            if (search_term in song['title'].lower() or 
                search_term in song['artist'].lower()):
                filtered_songs.append(song)
        else:
            filtered_songs.append(song)
            
    return filtered_songs

# run similarity script
def run_similarity_script(center_node, weights, num_results=10):
    try:
        weights_str = str(weights).replace(' ', '')
        
        # Run the similarity script with center_node and weights
        result = subprocess.run(
            ["python3", "scripts/similarity.py", center_node, weights_str, str(num_results)], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            st.error(f"Script failed with error: {result.stderr}")
            return None
        
        # Parse CSV result
        try:
            return pd.read_csv(io.StringIO(result.stdout))
        except Exception as e:
            st.error(f"Failed to parse results: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"Error running similarity script: {str(e)}")
        return None

# Load songs
all_songs = load_songs()

# Create search box and song selection
col1, col2 = st.columns([3, 1])

with col1:
    search_term = st.text_input("Search Songs or Artists")
    
# Filter songs based on search and year range
filtered_songs = filter_songs(
    all_songs, 
    search_term, 
    years_range[0], 
    years_range[1], 
    include_unknown
)

# Create song selection dropdown
song_options = {f"{song['artist']} - {song['title']} ({song['year']})": song['id'] 
                for song in filtered_songs}

# If no songs match filter, show message
if not song_options:
    st.warning("No songs match your filters. Try adjusting your search or year range.")
    selected_song_id = DEFAULT_CENTER_NODE
else:
    # Find default selection (Rick Astley or first song)
    default_option = next(
        (f"{song['artist']} - {song['title']} ({song['year']})" 
         for song in filtered_songs if song['id'] == DEFAULT_CENTER_NODE), 
        next(iter(song_options.keys()))
    )
    
    selected_song = st.selectbox(
        "Select Center Song", 
        options=list(song_options.keys()),
        index=list(song_options.keys()).index(default_option) if default_option in song_options else 0
    )
    
    selected_song_id = song_options[selected_song]

# Store the current state in session state
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = {
        'song_id': None,
        'weights': None,
        'results': None
    }

# Run analysis automatically on first load with Rick Astley as the default
if st.session_state.last_analysis['song_id'] is None:
    # Use Rick Astley's song and default weights for initial load
    initial_results = run_similarity_script(DEFAULT_CENTER_NODE, DEFAULT_WEIGHTS, 10)
    if initial_results is not None:
        st.session_state.last_analysis = {
            'song_id': DEFAULT_CENTER_NODE,
            'weights': DEFAULT_WEIGHTS.copy(),
            'results': initial_results
        }

# Custom button to run the analysis
run_analysis = st.button("Find Similar Songs") 

# Run analysis when button is clicked or we have initial results
if run_analysis or st.session_state.last_analysis['song_id'] is not None:
    # If button was clicked, update with current selections
    if run_analysis:
        with st.spinner("Analyzing musical similarity..."):
            results = run_similarity_script(selected_song_id, weights, 10)
            
            if results is not None and not results.empty:
                st.session_state.last_analysis = {
                    'song_id': selected_song_id,
                    'weights': weights.copy(),
                    'results': results
                }
    
    # Use the latest results (either from button click or initial load)
    if st.session_state.last_analysis['results'] is not None:
        results = st.session_state.last_analysis['results']
        
        # Create a 75%/25% column layout
        left_col, right_col = st.columns([3, 1])  # 75%/25% split
        
        with left_col:
            # Pyvis visualization
            st.subheader("Similarity Network Visualization")
            
            # Create nodes for visualization
            center_song = next((song for song in all_songs if song['id'] == st.session_state.last_analysis['song_id']), None)
            
            if center_song:
                # Pyvis network graph
                net = Network(height="700px", width="100%", bgcolor="#f8f9fa", font_color="#333")
                
                # center node
                center_label = f"{center_song['artist']} - {center_song['title']}"
                net.add_node(0, 
                           label=center_label, 
                           title=f"{center_label}<br>Year: {center_song['year']}<br>Similarity: 1.0", 
                           color="#ff3e96", 
                           size=35,  # Larger size
                           shape="dot",
                           font={'size': 16, 'face': 'Arial', 'color': 'black', 'strokeWidth': 3, 'strokeColor': '#ffffff'},
                           borderWidth=3,
                           borderWidthSelected=5,
                           shadow=True,
                           fixed=True,
                           x=0,
                           y=0)
                
                # position in a circle around the center
                num_nodes = len(results)
                radius = 300  
                
                # Similar Song Nodes
                for i, row in enumerate(results.iterrows(), start=1):
                    node_id = i
                    idx, song_data = row
                    song_label = f"{song_data['artist_name']} - {song_data['song_title']}"
                    similarity = float(song_data['weighted_similarity'])
                    
                    # Calc position
                    angle = 2 * math.pi * (i - 1) / num_nodes
                    x_pos = radius * math.cos(angle)
                    y_pos = radius * math.sin(angle)
                    
                    # Calc node size (this is similarity score-based)
                    node_size = 20 + (similarity * 15)
                    
                    # Node Coloring (this is also = similarity score-based)
                    node_color = f"rgba(30, 144, 255, {min(1.0, similarity + 0.2)})"
                    
                    # Add node
                    net.add_node(node_id, 
                               label=song_label, 
                               title=f"{song_label}<br>Year: {song_data['year']}<br>Similarity: {similarity:.3f}", 
                               color=node_color, 
                               size=node_size,
                               shape="dot",
                               font={'size': 14, 'face': 'Arial', 'color': 'black', 'strokeWidth': 2, 'strokeColor': '#ffffff'},
                               borderWidth=2,
                               shadow=True,
                               x=x_pos,
                               y=y_pos)
                    
                    edge_width = 1 + (similarity * 8)
                    net.add_edge(0, node_id, 
                                value=similarity * 10, 
                                title=f"Similarity: {similarity:.3f}",
                                width=edge_width,
                                color={'color': 'rgba(100,100,100,0.8)', 'highlight': '#ff3e96'})
                
                # Set net options
                net.set_options("""
                const options = {
                    "nodes": {
                        "font": {
                            "bold": true,
                            "background": "rgba(255,255,255,0.8)",
                            "strokeWidth": 2
                        }
                    },
                    "physics": {
                        "enabled": false
                    },
                    "edges": {
                        "smooth": {
                            "enabled": true,
                            "type": "dynamic",
                            "roundness": 0.5
                        },
                        "scaling": {
                            "min": 1,
                            "max": 10
                        }
                    },
                    "interaction": {
                        "hover": true,
                        "tooltipDelay": 200,
                        "navigationButtons": true,
                        "keyboard": true,
                        "zoomView": true
                    },
                    "layout": {
                        "improvedLayout": true,
                        "randomSeed": 42
                    }
                }
                """)
                
                # temp file to save the HTML
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
                    network_path = Path(tmp.name)
                    net.save_graph(str(network_path))
                    
                # Read HTML 
                with open(network_path, 'r') as f:
                    html_data = f.read()
                
                # Display network
                st.components.v1.html(html_data, height=750)
                
                # Clean up temp file
                network_path.unlink()
                
                # Add YouTube links
                st.subheader("Watch Similar Songs on YouTube")
                
                if len(results) > 0:
                    # Add some spacing and a divider
                    st.markdown("---")
                    
                    for i, (idx, song) in enumerate(results.iterrows()):
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"**{i+1}. {song['artist_name']} - {song['song_title']}** ({song['year']})")
                        
                        with col2:
                            search_query = f"{song['artist_name']} {song['song_title']}"
                            youtube_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                            st.markdown(f"[🎬 Watch on YouTube]({youtube_url})")
                        
                        if i < len(results) - 1:  # Add a lighter divider between songs
                            st.markdown("<hr style='margin: 5px 0; border: 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
            else:
                st.error("Could not find center song data")
        
        with right_col:
            # Results table
            st.subheader("Similar Songs")
            
            # Format results table
            results['rank'] = results['rank'].astype(int) + 1  # Make rank 1-based
            results['weighted_similarity'] = results['weighted_similarity'].astype(float).round(3)
            
            display_df = results.copy()
            display_df = display_df.rename(columns={
                'rank': 'Rank',
                'artist_name': 'Artist',
                'song_title': 'Song',
                'year': 'Year',
                'weighted_similarity': 'Similarity'
            })
            
            # Show results table
            st.dataframe(
                display_df[['Artist', 'Song', 'Similarity']],
                hide_index=True,
                use_container_width=True
            )
else:
    st.info("Click 'Find Similar Songs' to run the analysis.")

# Add information about the app
with st.expander("About this app"):
    st.markdown("""
    ## Music Similarity Visualization
    
    This app helps you discover songs similar to ones you like based on various musical features:
    
    - **Loudness**: Audio volume characteristics
    - **Pitches**: Musical notes and their patterns
    - **Timbre**: Sound quality and texture
    - **Genre**: Musical categorization
    - **Artist Similarity**: Connection between artists
    
    You can adjust the weights of these features to customize your recommendations.
    
    ### How it works
    1. Select a center song
    2. Adjust feature weights if desired
    3. Click "Find Similar Songs"
    4. Explore the similar songs network visualization
    
    The network visualization shows the center song and its connections to similar songs,
    with thicker lines representing stronger similarity.
    """)
