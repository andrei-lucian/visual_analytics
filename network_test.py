import json
import networkx as nx
import community as community_louvain
import dash
from dash import dcc, html
import plotly.graph_objects as go

# Load your JSON file and build the graph
with open("mc1.json", "r") as f:
    data = json.load(f)

G = nx.node_link_graph(data)
G = G.to_undirected()

desired_edge_types = ["Event.Fishing.OverFishing", "Event.Fishing.SustainableFishing"]

# Filter edges by desired types (include keys)
filtered_edges = [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if d.get("type") in desired_edge_types]

# Create subgraph with filtered edges
G_filtered = G.edge_subgraph(filtered_edges).copy()

# Community detection
partition = community_louvain.best_partition(G_filtered)
nx.set_node_attributes(G_filtered, partition, "community")

# Prepare node positions with spring layout (fixed seed for reproducibility)
pos = nx.spring_layout(G_filtered, seed=42)

# Prepare node scatter for plotly
node_x, node_y, node_text, node_color = [], [], [], []
for node in G_filtered.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(f"Node: {node}<br>Community: {partition[node]}")
    node_color.append(partition[node])

# Map edge types to colors
color_map = {
    "Event.Fishing.OverFishing": "red",
    "Event.Fishing.SustainableFishing": "green",
}

# Get all edge types present in filtered graph
edge_types_in_graph = set(d.get("type") for _, _, d in G_filtered.edges(data=True))

# Create edge traces grouped by edge type
edge_traces = []
for etype in edge_types_in_graph:
    edge_x = []
    edge_y = []
    for u, v, data in G_filtered.edges(data=True):
        if data.get("type") == etype:
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2, color=color_map.get(etype, "gray")),
        hoverinfo="text",
        mode="lines",
        name=etype,
        text=[etype] * (len(edge_x) // 3),  # optional hover text
    )
    edge_traces.append(edge_trace)

# Node trace (community colored)
node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode="markers",
    hoverinfo="text",
    text=node_text,
    marker=dict(
        showscale=True,
        colorscale="Viridis",
        color=node_color,
        size=15,
        colorbar=dict(thickness=15, title="Community", xanchor="left", title_side="right"),
        line_width=2,
    ),
)

# Build figure with edge traces + node trace
fig = go.Figure(
    data=edge_traces + [node_trace],
    layout=go.Layout(
        title="Community Clustering in Knowledge Graph Colored by Edge Type",
        title_font_size=16,
        showlegend=True,
        hovermode="closest",
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[dict(text="", showarrow=False, xref="paper", yref="paper")],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    ),
)

# Dash app
app = dash.Dash(__name__)

app.layout = html.Div([dcc.Graph(id="network-graph", figure=fig)])

if __name__ == "__main__":
    app.run(debug=True)
