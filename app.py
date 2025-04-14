from flask import Flask, jsonify, request, render_template, send_from_directory
import subprocess
import os
import sys
import json
import csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data/<filename>')
def get_data(filename):
    return send_from_directory('data', filename)

@app.route('/run_script', methods=['GET'])
def run_script():
    try:
        center_node = request.args.get('center_node', "SOCWJDB12A58A776AF")
        
        # Get weights from request parameters (default to [1,1,1,1,2] if not provided)
        weights = []
        for i in range(1, 6):
            weight = request.args.get(f'weight{i}', None)
            if weight is not None:
                weights.append(float(weight))
        
        # If weights weren't provided or were incomplete, use default
        if len(weights) != 5:
            weights = [1, 1, 1, 1, 2]  # Default weights
            
        # Format weights as string for command line
        weights_str = str(weights).replace(' ', '')
        
        # Run the similarity script with the center_node and weights
        result = subprocess.run(
            ["python3", "scripts/similarity.py", center_node, weights_str], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': f'Script failed with error: {result.stderr}'
            }), 500
        
        return result.stdout
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

# Add a new endpoint to get song list
@app.route('/get_songs', methods=['GET'])
def get_songs():
    try:
        songs = []
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'artist_id_and_name.csv')
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Return all songs instead of limiting to 100
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
        
        return jsonify(songs)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)