import plotly.express as px
import dash
from dash import dcc, html
import pandas as pd
import json
import plotly.graph_objects as go

# Replace 'your_file.json' with your actual file path
with open('mc1.json', 'r') as f:
    data = json.load(f)

# Extract the nodes list
nodes = data["nodes"]
links = data["links"]

# Create a DataFrame from nodes
df_nodes = pd.DataFrame(nodes)
df_links = pd.DataFrame(links)

filtered_df = df_links[df_links['target'] == 'Smith-Hull'] # Add callback from scatter

df_baseline = filtered_df[filtered_df['_algorithm'] == 'BassLine']
df_shadgpt = filtered_df[filtered_df['_algorithm'] == 'ShadGPT']

# Get all unique types from the whole df_links
all_types = df_links['type'].unique()

# Get counts per algorithm as Series
counts_baseline = df_baseline['type'].value_counts()
counts_shadgpt = df_shadgpt['type'].value_counts()

# Convert counts to dict and fill missing types with 0
def counts_to_full_dict(counts, all_types):
    return {t: counts.get(t, 0) for t in all_types}

counts_baseline_full = counts_to_full_dict(counts_baseline, all_types)
counts_shadgpt_full = counts_to_full_dict(counts_shadgpt, all_types)

# Create DataFrame with one row per algorithm
df_plot = pd.DataFrame([counts_baseline_full, counts_shadgpt_full])
df_plot['_algorithm'] = ['BassLine', 'ShadGPT']
df_plot['_algorithm_code'] = df_plot['_algorithm'].map({'BassLine': 0, 'ShadGPT': 1})

dimensions = []
for col in all_types:
    max_val = df_plot[col].max()
    if max_val == 0:
        max_val = 1  # prevent zero range error
    dimensions.append(dict(
        range=[0, max_val],
        label=col,
        values=df_plot[col]
    ))

fig = go.Figure(data=go.Parcoords(
    line=dict(color=df_plot['_algorithm_code'], colorscale='Portland', showscale=True),
    dimensions=dimensions
))

# Dash app setup
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H2("Parallel Coordinates Plot: BassLine vs ShadGPT (Scaled 0 to Max)"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run(debug=True)