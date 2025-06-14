import networkx as nx
import community.community_louvain as community_louvain
import plotly.graph_objects as go
from dash import dcc


class KnowledgeGraphPlot:
    def __init__(self, data, html_id):
        self.data = data
        self.edge_types_available = self._get_edge_types()
        self.color_map = self._generate_color_map()
        self.html_id = html_id

    def _get_edge_types(self):
        G = nx.node_link_graph(self.data, edges="links")
        return list({d.get("type") for _, _, d in G.edges(data=True)})

    def _generate_color_map(self):
        from itertools import cycle

        colors = cycle(["red", "green", "blue", "orange", "purple", "brown", "cyan", "magenta", "gray"])
        return {etype: next(colors) for etype in self.edge_types_available}

    def build_graph(self, selected_types):
        G = nx.node_link_graph(self.data, edges="links").to_undirected()
        filtered_edges = [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if d.get("type") in selected_types]
        return G.edge_subgraph(filtered_edges).copy()

    def generate_figure(self, selected_types, highlight_node_id=None):
        G_filtered = self.build_graph(selected_types)

        # Example shapes for types
        type_to_shape = {
            "Entity.Organization.FishingCompany": "star",
            "Entity.Organization.Company": "square",
            "Entity.Organization.LogisticsCompany": "diamond",
            "Entity.Organization.NGO": "triangle-up",
            "Entity.Organization": "cross",
        }

        color_map = {
            "Entity.Organization.FishingCompany": "blue",
            "Entity.Organization.Company": "green",
            "Entity.Organization.LogisticsCompany": "orange",
            "Entity.Organization.NGO": "purple",
            "Entity.Organization": "red",
        }

        # Types to disable interactivity (example)
        non_interactive_types = {"Entity.Person", "Entity.Location.Region", "Entity.Organization.GovernmentOrg"}

        # Collect nodes by type
        nodes_by_type = {}
        for node, attrs in G_filtered.nodes(data=True):
            ctype = attrs.get("type", "Unknown")
            nodes_by_type.setdefault(ctype, []).append(node)

        if len(G_filtered.nodes) == 0:
            return go.Figure(layout={"title": "No edges match the selected types."})

        pos = nx.spring_layout(G_filtered, seed=42)
        partition = community_louvain.best_partition(G_filtered)
        nx.set_node_attributes(G_filtered, partition, "community")

        edge_traces = []
        for etype in selected_types:
            edge_x, edge_y = [], []
            for u, v, d in G_filtered.edges(data=True):
                if d.get("type") == etype:
                    x0, y0 = pos[u]
                    x1, y1 = pos[v]
                    edge_x += [x0, x1, None]
                    edge_y += [y0, y1, None]
            edge_traces.append(
                go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    line=dict(width=2, color=self.color_map.get(etype, "gray")),
                    mode="lines",
                    name=etype,
                    hoverinfo="skip",
                    text=[etype] * (len(edge_x) // 3),
                )
            )

        node_x, node_y, node_text, node_color = [], [], [], []
        for node in G_filtered.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Node: {node}<br>Community: {partition[node]}")
            node_color.append(partition[node])

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            hoverinfo="text",
            text=node_text,
            marker=dict(
                showscale=False,
                colorscale="Viridis",
                color=node_color,
                size=15,
                colorbar=dict(title="Community"),
                line_width=2,
            ),
            showlegend=False,
        )

        fig = go.Figure(data=edge_traces + [node_trace])
        fig.update_layout(
            title="Knowledge Graph (Filtered by Edge Type)",
            title_font_size=16,
            showlegend=True,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )

        node_traces = []

        for ctype, nodes in nodes_by_type.items():
            x_vals, y_vals, hover_texts, sizes, colors, line_colors = [], [], [], [], [], []

            for n in nodes:
                x, y = pos[n]
                x_vals.append(x)
                y_vals.append(y)
                hover_texts.append(f"Node: {n}<br>Type: {ctype}")

                is_highlighted = n == highlight_node_id

                sizes.append(22 if is_highlighted else 15)
                colors.append(color_map.get(ctype, "pink"))
                line_colors.append("black" if not is_highlighted else "gold")

            is_interactive = ctype not in non_interactive_types

            node_traces.append(
                go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode="markers",
                    hoverinfo="text" if is_interactive else "skip",
                    text=hover_texts if is_interactive else None,
                    marker=dict(
                        size=sizes,
                        color=colors,
                        symbol=type_to_shape.get(ctype, "circle"),
                        line=dict(width=2, color=line_colors),
                        opacity=1,  # Make sure opacity is not lowered
                    ),
                    showlegend=True,
                    name=ctype,
                )
            )
        fig = go.Figure(data=edge_traces + node_traces)
        return fig

    def get_edge_type_options(self):
        return [{"label": etype, "value": etype} for etype in self.edge_types_available]

    def render(self):
        # Initially show all edge types
        fig = self.generate_figure(self.edge_types_available)
        return dcc.Graph(id=self.html_id, figure=fig)
