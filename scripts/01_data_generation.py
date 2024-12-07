# %%
import json
from flask import jsonify
import sqlite3
import pandas as pd
DATABASE_PATH = '../database/abundances.db'
element_list = ['Fe', 'Ti', 'Ca', 'Si', 'Al', 'Mg', 'Na'] + \
    ['Plagioclase Feldspar', 'Olivine', 'Ilmenite', 'Armalcolite']

# %%


# %%


# %%

# %%
df2 = pd.read_csv('../data/merged_data.csv')
# Rename column
df2.rename(columns={'lon': 'long'}, inplace=True)

# Ensure timestamp is in datetime format
df2['timestamp_dt'] = pd.to_datetime(df2['timestamp'])

# Extract components and create new columns
df2['year'] = df2['timestamp_dt'].dt.year
df2['day'] = df2['timestamp_dt'].dt.day
df2['hour'] = df2['timestamp_dt'].dt.hour
df2['min'] = df2['timestamp_dt'].dt.minute
df2['sec'] = df2['timestamp_dt'].dt.second


list1 = element_list+['date', 'timestamp', 'lat',
                      'long', 'year', 'day', 'hour', 'min', 'sec']
df2[list1]

df1 = df2


df1.head()

# %%
df1.shape

# %%


# %%


# %%
df1.columns

# %%
df1

# %%
# Save to CSV
# df1.to_csv('raw_data.csv', index=False)

# %%
# df_loaded = pd.read_csv('data.csv')

# %%


def query_db(query, params=()):
    db_path = DATABASE_PATH
    connection = sqlite3.connect(db_path)

    # Using pandas to read the query result directly into a DataFrame
    df = pd.read_sql_query(query, connection, params=params)

    connection.close()

    # Convert DataFrame to a list of dictionaries and return it
    result_list = df.to_dict(orient='records')

    return result_list


# %%
DATABASE_PATH

# %%


def query_modify_df(query, params=()):
    """Helper function to execute a SQL query and return results."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    connection.close()
    return results


# %%
DATABASE_PATH

# %%


def create_database(db_path):
    """Creates an SQLite database if it doesn't exist."""
    try:
        # Establish a connection (creates the file if it doesn't exist)
        connection = sqlite3.connect(db_path)
        print(f"Database created at {db_path}")
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
    finally:
        # Close the connection after creation
        connection.close()


# Example usage
create_database(DATABASE_PATH)


# %%
LONGDF = None

# %%


def create_abundance_table(df, element_list, overwrite=False):
    """
    Creates and populates an `abundances` table in SQLite with additional columns.

    Args:
        df (pd.DataFrame): DataFrame containing element abundance data and other columns.
        element_list (list): List of elements to extract from the DataFrame.
        overwrite (bool): If True, the table will be dropped and recreated.
    """
    # Step 1: Prepare the database and table
    if overwrite:
        query_modify_df("DROP TABLE IF EXISTS abundances;")

    # Create table if not exists with all required columns
    create_table_query = """
    CREATE TABLE abundances (
        element TEXT NOT NULL,
        date TEXT,
        abundance REAL NOT NULL,
        lat REAL,
        long REAL,
        year INTEGER,
        day INTEGER,
        hour INTEGER,
        min INTEGER,
        sec INTEGER
    );
    """
    query_modify_df(create_table_query)

    # Step 2: Transform DataFrame into a long format for SQL insertion
    long_df = pd.melt(df, id_vars=['date', 'lat', 'long', 'year', 'day', 'hour', 'min', 'sec'],
                      value_vars=element_list, var_name='element', value_name='abundance')
    long_df['date'] = long_df['date'].astype(str)

    # global LONGDF
    # LONGDF = long_df
    # Step 3: Insert data into the database
    insert_query = """
    INSERT INTO abundances (element, date, abundance, lat, long, year, day, hour, min, sec) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    data_to_insert = long_df[['element', 'date', 'abundance', 'lat',
                              'long', 'year', 'day', 'hour', 'min', 'sec']].values.tolist()

    # Execute inserts in a batch
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.executemany(insert_query, data_to_insert)
    connection.commit()
    connection.close()


# Example usage:
create_abundance_table(df1, element_list, overwrite=False)


# %%
DATABASE_PATH

# %%
df1.date.value_counts()

# %%


def query_db(query, params=()):
    db_path = DATABASE_PATH
    connection = sqlite3.connect(db_path)

    # Using pandas to read the query result directly into a DataFrame
    df = pd.read_sql_query(query, connection, params=params)

    connection.close()

    # Convert DataFrame to a list of dictionaries
    result_list = df.to_dict(orient='records')

    return result_list


# Example of querying the database for a specific element
element = "Si"  # Example element (replace with your query parameter)
# date = None # Example date (can be None or a valid date)
date = "2021-04-22"  # Example date (can be None or a valid date)
# date = "2020-01-02"  # Example date (can be None or a valid date)

# Build the query based on the presence of 'date'
if date:
    query = "SELECT * FROM abundances WHERE element = ? AND date = ?"
    data = (element, date)
else:
    query = "SELECT * FROM abundances WHERE element = ?"
    data = (element,)

# Get the result from the query_db function
result = query_db(query, data)

# Print the result in JSON-like format (list of dictionaries)
print(json.dumps(result, indent=4))
