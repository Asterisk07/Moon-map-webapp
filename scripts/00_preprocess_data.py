# %%
# %%
import json
from flask import jsonify
import sqlite3
import pandas as pd
DATABASE_PATH = '../database/abundances.db'
element_list = ['Fe', 'Ti', 'Ca', 'Si', 'Al', 'Mg', 'Na']

# %%


# %%


# %%

# %%
df2 = pd.read_csv('../data/element_data.csv')
df3 = pd.read_csv('../data/compound_data.csv')

# %%
df2.columns

# %%
df3.columns

# %%
df2.shape

# %%
# Merge the DataFrames
merged_df = pd.merge(
    df3, df2, on=['lat', 'lon', 'date', 'timestamp'], how='inner')

# %%
merged_df.shape

# %%
df3.shape

# %%
merged_df.to_csv('../data/merged_data.csv', index=False)
