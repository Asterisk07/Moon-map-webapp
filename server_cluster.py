import json
from flask import Flask, request, jsonify, render_template
import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from functools import lru_cache
import math
from time import perf_counter_ns

# Removed unused imports like subprocess

# FETCH_LIMIT = 2000
FETCH_LIMIT = None

# DATABASE_PATH = 'database/abundances_old.db'
# DATABASE_PATH = 'database/abundances_new.db'
DATABASE_PATH = 'database/abundances.db'

MAX_CLUSTERS = 5000
MIN_CLUSTERS = 1000
CACHE_SIZE = 32  # Number of recent results to cache


def fetch_points_for_tile(x, y, zoom):
    bbox = tile_to_bbox(x, y, zoom)
    conn = sqlite3.connect('spatial_data.db')
    query = """
    SELECT id, minX AS lon, minY AS lat FROM points
    WHERE minX BETWEEN ? AND ? AND minY BETWEEN ? AND ?;
    """
    cursor = conn.execute(query, (bbox[0], bbox[2], bbox[1], bbox[3]))
    points = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'lat': row[1], 'lon': row[2]} for row in points]


# import os
# script_dir = os.path.dirname(os.path.abspath(__file__))
# os.chdir(script_dir)
app = Flask(__name__)
# app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/fetch_points')
def fetch_points():
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    zoom = int(request.args.get('z'))
    points = fetch_points_for_tile(x, y, zoom)
    return jsonify(points)


# def query_db(query, params=()):
#     db_path = DATABASE_PATH
#     connection = sqlite3.connect(db_path)
#     connection.row_factory = sqlite3.Row  # To return results as dictionaries
#     cursor = connection.cursor()

#     cursor.execute(query, params)
#     results = cursor.fetchall()

#     connection.close()
#     # Convert rows to dictionaries for JSON response
#     return [dict(row) for row in results]

# Route to serve the index.html file


@app.route('/')
def index():
    # return render_template('index with infobox.html')
    return render_template('index_cluster.html')


@app.route('/run-python', methods=['POST'])
def run_python_script():
    raise Exception("Not implemented")

# def query_db(query, params=(), limit=FETCH_LIMIT):
#     db_path = DATABASE_PATH
#     connection = sqlite3.connect(db_path)


def query_db(query, params=()):
    print(f"\nExecuting query with params: {params}")
    print(f"Query: {query}")

    db_path = DATABASE_PATH
    try:
        with sqlite3.connect(db_path) as connection:
            start_time = perf_counter_ns()
            # Add LIMIT clause if a limit is specified
            if FETCH_LIMIT is not None:
                query += f" LIMIT {FETCH_LIMIT}"
            df = pd.read_sql_query(query, connection, params=params)
            query_time = (perf_counter_ns() - start_time) / 1e6

        if df.empty:
            print("Query returned no results")
            return []

        print(f"Query returned {len(df)} rows in {query_time:.2f}ms")
        print("Sample data:", df.iloc[0].to_dict()
              if len(df) > 0 else "No data")
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []


@lru_cache(maxsize=CACHE_SIZE)
def cached_cluster_data(data_key, n_clusters):
    """Cached version of clustering to avoid recomputing for same parameters"""
    return cluster_data(json.loads(data_key), n_clusters)


def estimate_clusters(data_length, zoom_level=None):
    """Estimate optimal number of clusters based on data size and zoom"""
    if zoom_level is None:
        # Base number of clusters on data size
        return min(MAX_CLUSTERS, max(MIN_CLUSTERS, math.ceil(data_length / 50)))
    else:
        # Adjust clusters based on zoom level
        base_clusters = math.ceil(data_length / 50)
        # Adjust clusters based on zoom
        zoom_factor = math.pow(2, zoom_level - 2)
        return min(MAX_CLUSTERS, max(MIN_CLUSTERS, math.ceil(base_clusters * zoom_factor)))


def cluster_data(data, n_clusters=None):
    print(f"\nStarting clustering of {len(data)} points")

    # Estimate clusters if not specified
    n_clusters = n_clusters or estimate_clusters(len(data))

    if len(data) <= n_clusters:
        print("No clustering needed, data points <= n_clusters")
        return data

    start_time = perf_counter_ns()
    coords = np.array([[d['lat'], d['long']] for d in data])
    values = np.array([d.get('abundance', d.get('ratio', 0)) for d in data])

    print(f"Running KMeans clustering with {n_clusters} clusters")
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        # Larger batch size for faster processing
        batch_size=min(10000, len(data)),
        max_iter=100,                       # Limit iterations
        init_size=min(10000, len(data)),   # Smaller init sample
        random_state=42                     # For consistent results
    )

    # Process in batches for large datasets
    cluster_labels = kmeans.fit_predict(coords)

    clustered_data = []
    for i in range(n_clusters):
        mask = cluster_labels == i
        if np.any(mask):
            cluster_points = coords[mask]
            cluster_values = values[mask]
            center = cluster_points.mean(axis=0)
            mean_value = cluster_values.mean()

            # Get sample point for element info
            sample_point = next(
                p for p in data if p['lat'] == coords[mask][0][0] and p['long'] == coords[mask][0][1])

            cluster_point = {
                'lat': float(center[0]),
                'long': float(center[1]),
                'abundance': float(mean_value),
                'ratio': float(mean_value),
                # Preserve element information
                'element': sample_point.get('element'),
                'element1': sample_point.get('element1'),
                'element2': sample_point.get('element2'),
                'abundance1': sample_point.get('abundance1'),
                'abundance2': sample_point.get('abundance2')
            }
            clustered_data.append(cluster_point)

    cluster_time = (perf_counter_ns() - start_time) / \
        1e6  # Convert to milliseconds
    print(f"Clustering completed in {cluster_time:.2f}ms")
    print(f"Reduced {len(data)} points to {len(clustered_data)} clusters")

    return clustered_data


def normalize_longitude(lng):
    """Normalize longitude to [-180, 180] range"""
    return ((lng + 180) % 360) - 180


@app.route('/abundance', methods=['GET'])
def get_abundance():
    element = request.args.get('element')
    plot_type = request.args.get('plotType', 'clusters')
    date = request.args.get('date')

    if not element or element == 'undefined':
        return jsonify({"error": "Element parameter is required"}), 400

    try:
        if date:
            query = """
                SELECT lat, long, abundance, element, date
                FROM abundances
                WHERE element = ? AND date = ?
            """
            result = query_db(query, (element, date))
        else:
            query = """
                SELECT lat, long, abundance, element, date
                FROM abundances
                WHERE element = ?
            """
            result = query_db(query, (element,))

        if not result:
            print(f"No data found for element: {element}")
            return jsonify([])

        # Only cluster if plot_type is 'clusters'
        if plot_type == 'clusters':
            result = cluster_data(result)

        print(f"Found {len(result)} points for {element}")
        return jsonify(result)

    except Exception as e:
        print(f"Error in get_abundance: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ratio', methods=['GET'])
def get_ratio():
    element1 = request.args.get('element')
    element2 = request.args.get('element2')
    plot_type = request.args.get('plotType', 'clusters')

    if not element1 or not element2:
        return jsonify({"error": "Both elements are required"}), 400

    try:
        query = """
            SELECT 
                a1.lat, 
                a1.long, 
                CAST(a1.abundance AS FLOAT) / CAST(a2.abundance AS FLOAT) as ratio,
                a1.abundance as abundance1,
                a2.abundance as abundance2,
                a1.element as element1,
                a2.element as element2
            FROM abundances a1
            JOIN abundances a2 
            ON a1.lat = a2.lat 
            AND a1.long = a2.long
            WHERE a1.element = ? 
            AND a2.element = ?
        """
        result = query_db(query, (element1, element2))

        if not result:
            print(f"No data found for ratio {element1}/{element2}")
            return jsonify([])

        # Only cluster if plot_type is 'clusters'
        if plot_type == 'clusters':
            result = cluster_data(result)

        print(f"Found {len(result)} ratio points")
        return jsonify(result)

    except Exception as e:
        print(f"Error in get_ratio: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/histogram', methods=['GET'])
def get_histogram():
    element = request.args.get('element')
    date = request.args.get('date')

    if not element:
        return jsonify({"error": "Element parameter is required"}), 400

    try:
        if date:
            query = """
                SELECT abundance
                FROM abundances
                WHERE element = ? AND date = ?
            """
            result = query_db(query, (element, date))
        else:
            query = """
                SELECT abundance
                FROM abundances
                WHERE element = ?
            """
            result = query_db(query, (element,))

        if not result:
            return jsonify([0] * 10)  # Return empty histogram

        # Calculate histogram bins (10 bins)
        abundances = [r['abundance'] for r in result]
        total = len(abundances)
        if total == 0:
            return jsonify([0] * 10)

        hist, _ = np.histogram(abundances, bins=10, range=(0, 50))
        # Convert to percentages
        hist = (hist / total) * 100
        return jsonify(hist.tolist())

    except Exception as e:
        print(f"Error generating histogram: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=1234)
