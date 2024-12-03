import json
import subprocess
from flask import Flask, request, jsonify, render_template
import sqlite3
import pandas as pd
FETCH_LIMIT = 50
# FETCH_LIMIT = None

# DATABASE_PATH = 'database/abundances_old.db'
DATABASE_PATH = 'database/abundances.db'


# import os
# script_dir = os.path.dirname(os.path.abspath(__file__))
# os.chdir(script_dir)

app = Flask(__name__)
# app = Flask(__name__, static_folder='.', static_url_path='')


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


# Route to serve the index.html file


@app.route('/')
def index():
    return render_template('index.html')
    # return app.send_static_file('index copy.html') #no async
    # return app.send_static_file('index_async.html')  # no async
    # return app.send_static_file('index.html')
    # return app.send_static_file('index.html')

# @app.route('/run-python', methods=['POST'])
# def run_python_script():
#     data = request.json
#     year = data.get('arg1')
#     # month = data.get('arg2')

#     result = subprocess.run(
#         ['python', 'script.py', year, month],
#         capture_output=True,
#         text=True
#     )


@app.route('/run-python', methods=['POST'])
def run_python_script():
    raise Exception("Not implemented")
    # Get arguments from request
    # data = request.json
    # year = data.get('arg1')
    # month = data.get('arg2')

    # # Call the function directly and return the result
    # result = get_moonquake_data(year, month)
    # return jsonify(result)

    # Parse and return JSON output
    # output = json.loads(result.stdout)
    # return jsonify(output)


@app.route('/abundance', methods=['GET'])
def get_abundance():
    element = request.args.get('element')
    date = request.args.get('date')  # Optional parameter

    if not element or element == 'undefined':
        return jsonify({"error": "Element parameter is required"}), 400

    print(f"Fetching for: element={element}, date={date}")

    try:
        if date:
            query = "SELECT * FROM abundances WHERE element = ? AND date = ?"
            data = (element, date)
        else:
            query = "SELECT * FROM abundances WHERE element = ?"
            data = (element,)

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

    if not element1 or not element2:
        return jsonify({"error": "Both elements are required"}), 400

    if date:
        query = """
            SELECT a1.lat, a1.long, a1.abundance/a2.abundance as ratio, a1.date
            FROM abundances a1
            JOIN abundances a2 ON a1.lat = a2.lat AND a1.long = a2.long AND a1.date = a2.date
            WHERE a1.element = ? AND a2.element = ? AND a1.date = ?
        """
        data = (element1, element2, date)
    else:
        query = """
            SELECT a1.lat, a1.long, a1.abundance/a2.abundance as ratio, a1.date
            FROM abundances a1
            JOIN abundances a2 ON a1.lat = a2.lat AND a1.long = a2.long
            WHERE a1.element = ? AND a2.element = ?
        """
        data = (element1, element2)

    result = query_db(query, data)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=3000)
