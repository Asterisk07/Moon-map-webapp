import json
import subprocess
from flask import Flask, request, jsonify, render_template
import sqlite3
import pandas as pd
# FETCH_LIMIT = 1000
FETCH_LIMIT = None

# DATABASE_PATH = 'database/abundances_old.db'
DATABASE_PATH = 'database/abundances_new.db'
# DATABASE_PATH = 'database/abundances.db'


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
    return render_template('index.html')


@app.route('/run-python', methods=['POST'])
def run_python_script():
    raise Exception("Not implemented")


def query_db(query, params=(), limit=FETCH_LIMIT):
    db_path = DATABASE_PATH
    connection = sqlite3.connect(db_path)

    # Add LIMIT clause if a limit is specified
    if limit is not None:
        query += f" LIMIT {limit}"

    # Using pandas to read the query result directly into a DataFrame
    df = pd.read_sql_query(query, connection, params=params)

    connection.close()

    # Convert DataFrame to a list of dictionaries
    result_list = df.to_dict(orient='records')

    return result_list


@app.route('/abundance', methods=['GET'])
def get_abundance():
    element = request.args.get('element')
    date = request.args.get('date')  # Optional parameter

    # Parameters for bounding box (for zoom/pan)
    # Default to -90 if not provided
    lat_min = float(request.args.get('lat_min', -90))
    # Default to 90 if not provided
    lat_max = float(request.args.get('lat_max', 90))
    # Default to -180 if not provided
    long_min = float(request.args.get('long_min', -180))
    # Default to 180 if not provided
    long_max = float(request.args.get('long_max', 180))

    if not element or element == 'undefined':
        return jsonify({"error": "Element parameter is required"}), 400

    print(
        f"Fetching for: element={element}, date={date}, lat_min={lat_min}, lat_max={lat_max}, long_min={long_min}, long_max={long_max}")

    try:
        if date:
            query = """
                SELECT * FROM abundances
                WHERE element = ? AND date = ? 
                AND lat BETWEEN ? AND ? 
                AND long BETWEEN ? AND ?
            """
            data = (element, date, lat_min, lat_max, long_min, long_max)
        else:
            query = """
                SELECT * FROM abundances
                WHERE element = ? 
                AND lat BETWEEN ? AND ? 
                AND long BETWEEN ? AND ?
            """
            data = (element, lat_min, lat_max, long_min, long_max)

        result = query_db(query, data)
        if not result:
            return jsonify([])  # Return empty array if no results

        return jsonify(result)

    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500


@app.route('/ratio', methods=['GET'])
def get_ratio():
    element1 = request.args.get('element')
    element2 = request.args.get('element2')
    date = request.args.get('date')  # Optional parameter

    # Parameters for bounding box (for zoom/pan)
    # Default to -90 if not provided
    lat_min = float(request.args.get('lat_min', -90))
    # Default to 90 if not provided
    lat_max = float(request.args.get('lat_max', 90))
    # Default to -180 if not provided
    long_min = float(request.args.get('long_min', -180))
    # Default to 180 if not provided
    long_max = float(request.args.get('long_max', 180))

    if not element1 or not element2:
        return jsonify({"error": "Both elements are required"}), 400

    print(
        f"Fetching ratio for: element1={element1}, element2={element2}, date={date}, lat_min={lat_min}, lat_max={lat_max}, long_min={long_min}, long_max={long_max}")

    if date:
        query = """
            SELECT a1.lat, a1.long, a1.abundance/a2.abundance as ratio, 
                   a1.abundance as abundance1, a2.abundance as abundance2,
                   a1.date
            FROM abundances a1
            JOIN abundances a2 ON a1.lat = a2.lat AND a1.long = a2.long AND a1.date = a2.date
            WHERE a1.element = ? AND a2.element = ? AND a1.date = ?
            AND a1.lat BETWEEN ? AND ? 
            AND a1.long BETWEEN ? AND ?
        """
        data = (element1, element2, date, lat_min, lat_max, long_min, long_max)
    else:
        query = """
            SELECT a1.lat, a1.long, a1.abundance/a2.abundance as ratio,
                   a1.abundance as abundance1, a2.abundance as abundance2,
                   a1.date
            FROM abundances a1
            JOIN abundances a2 ON a1.lat = a2.lat AND a1.long = a2.long
            WHERE a1.element = ? AND a2.element = ?
            AND a1.lat BETWEEN ? AND ? 
            AND a1.long BETWEEN ? AND ?
        """
        data = (element1, element2, lat_min, lat_max, long_min, long_max)

    result = query_db(query, data)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=3000)
