# %%
from collections import defaultdict
from sklearn.cluster import KMeans
import numpy as np
from sklearn.neighbors import KDTree
import sys
import time
from flask import jsonify
import pandas as pd
import sqlite3
import json
DATABASE_PATH = '../database/abundances.db'
element_list = ['Fe', 'Ti', 'Ca', 'Si', 'Al', 'Mg', 'Na'] + \
    ['Plagioclase Feldspar', 'Olivine', 'Ilmenite', 'Armalcolite']

# %%
FETCH_LIMIT = None

# %%


def query_db(query, params=(), limit=None):
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


# %%
query = "SELECT * FROM abundances"
data = []

# %%

# %%
# Start the timer to measure the query execution time

start_time = time.time()

result = query_db(query, data, FETCH_LIMIT)


end_time = time.time()
# Print the time taken to perform the query
print(f"time to fetch : {end_time - start_time:.4f} seconds")

# %%
len(result) / 7

# %%


# %%


# Get the size of the variable
size_in_bytes = sys.getsizeof(result)

print(f"Size of my_list: {size_in_bytes//1024**2} MB")


# %%

points = result

# %%
# kernel = True

# %%
# Create a KDTree for each element
element_trees = {}
element_points_dict = {}

# Start the timer to measure the query execution time
start_time = time.time()

for element in element_list:
    # print("creating for element", element)
    element_points = [
        point for point in points if point['element'] == element]
    element_points_dict[element] = element_points
    element_points = [(point['lat'], point['long'])
                      for point in element_points]
    element_trees[element] = KDTree(np.array(element_points))

end_time = time.time()
# Print the time taken to perform the query
print(f"Trees creation time : {end_time - start_time:.4f} seconds")

# Query function


def get_nearby_points(query_point, radius_degrees, element):
    query_array = np.array([query_point])

    # Query the relevant tree for the specified element
    tree = element_trees.get(element)
    if tree:
        indices = tree.query_radius(query_array, r=radius_degrees)
        return [points[i] for i in indices[0]]
    else:
        return []


# %%
len(element_points_dict['Mg'])

# %% [markdown]
# ## inspecting dates

# %%
s1 = {point['date'] for point in points}
# Convert to a list
s1 = sorted(list(s1))
s1

# Save to JSON
with open("../static/dates.json", "w") as f:
    json.dump(s1, f, indent=4)

print("Unique dates saved to 'dates.json'.")

# %% [markdown]
# ## histograms

# %%
# Initialize a dictionary to store histogram data
histograms = {}

# Define bins
bins = np.arange(0, 51, 5)  # 0-10, 10-20, ..., 90-100

# Compute histograms with normalization
for element, points in element_points_dict.items():
    # Extract abundances
    abundances = [entry["abundance"] for entry in points]

    # Compute histogram counts
    counts, _ = np.histogram(abundances, bins=bins)

    # Normalize counts
    total = sum(counts)
    normalized_counts = (
        counts*100 / total).tolist() if total > 0 else counts.tolist()

    # Store the result in the histogram dictionary
    histograms[element] = normalized_counts

histograms


histograms

# %%
# Save to JSON
with open("../static/histograms.json", "w") as f:
    json.dump(histograms, f, indent=4)

print("Histograms computed and saved to 'histograms.json'.")

# %%


# %%


# %%
len(element_points)

# %%


# %%
# raise End

# %% [markdown]
# ## Clustering

# %%
# Perform clustering to create 2k spatial clusters
coordinates = element_points
print(len(coordinates))
n_clusters = 5000
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
labels = kmeans.fit_predict(coordinates)

# Save cluster labels and centers
cluster_centers = kmeans.cluster_centers_


# %%

# Initialize variables
M = len(element_points_dict)  # Number of elements
n_clusters = max(labels)+1  # Total distinct labels

# Create a structure to store the cluster means for each element
cluster_means_per_element = {
    element: [0] * n_clusters for element in element_points_dict}

# Iterate over each element and compute cluster means
for element, points in element_points_dict.items():
    # Create a list to store sums and counts for each cluster
    cluster_sums = [0] * n_clusters
    cluster_counts = [0] * n_clusters

    # Accumulate abundances for each cluster
    for point, label in zip(points, labels):
        cluster_sums[label] += point['abundance']
        cluster_counts[label] += 1

    # Compute means for each cluster
    cluster_means_per_element[element] = [
        cluster_sums[i] / cluster_counts[i] if cluster_counts[i] > 0 else 0 for i in range(n_clusters)
    ]

# Debug: Print a small sample of results
for element, means in cluster_means_per_element.items():
    # Print the first 10 clusters as a sample
    print(f"Cluster means for {element}: {means[:10]}")


# %%
cluster_means_per_element['Fe']

# %%
cluster_centers

# %%
# import json

# # Save the elementwise_cluster_data to a JSON file
# with open('static/{element}_clusters.json', 'w') as json_file:
#     json.dump(elementwise_cluster_data, json_file, indent=4)

# print("Data saved to 'elementwise_cluster_data.json'")


# %%
# Initialize a dictionary to store the final result
elementwise_cluster_data = {}

# Iterate through each element and its corresponding cluster means
for element, cluster_means in cluster_means_per_element.items():
    elementwise_cluster_data[element] = [
        {
            'element': element,
            'abundance': cluster_means[i],
            'lat': cluster_centers[i][0],  # Latitude of the cluster center
            'long': cluster_centers[i][1]  # Longitude of the cluster center
        }
        for i in range(len(cluster_centers))
    ]

# Example: Print the first cluster data for a specific element (e.g., 'Fe')
print(f"First cluster for Fe: {elementwise_cluster_data['Fe'][0]}")


# %%


# %%

# Save the elementwise_cluster_data to a JSON file
with open('../static/clusters.json', 'w') as json_file:
    json.dump(elementwise_cluster_data, json_file, indent=4)

print("Data saved to 'clusters.json'")


# %%
len(cluster_centers)

# %% [markdown]
# # End of file
