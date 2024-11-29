import pandas as pd
import sqlite3
from flask import Flask, request, jsonify, render_template
import subprocess
import json

# import os
# script_dir = os.path.dirname(os.path.abspath(__file__))
# os.chdir(script_dir)

app = Flask(__name__)
# app = Flask(__name__, static_folder='.', static_url_path='')

DATABASE_PATH = 'database/abundances.db'
# DATABASE_PATH = 'path/to/your/database.db'


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


def query_db(query, params=()):
    db_path = DATABASE_PATH
    connection = sqlite3.connect(db_path)

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
    print(f"fetching for : element{element}, date : {date}")

    if date:
        query = "SELECT * FROM abundances WHERE element = ? AND date = ?"
        data = (element, date)
    else:
        query = "SELECT * FROM abundances WHERE element = ?"
        data = (element,)

    # query_db is a helper function for querying SQLite
    result = query_db(query, data)
    print(result[0])
    result = jsonify(result)
    # print(result[0])
    return result


@app.route('/ratio', methods=['GET'])
def get_ratio():
    element1 = request.args.get('element1')
    element2 = request.args.get('element2')
    date = request.args.get('date')  # Optional parameter

    if date:
        query = "SELECT * FROM element_ratios WHERE element1 = ? AND element2 = ? AND date = ?"
        data = (element1, element2, date)
    else:
        query = "SELECT * FROM element_ratios WHERE element1 = ? AND element2 = ?"
        data = (element1, element2)

    result = query_db(query, data)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=3000)
