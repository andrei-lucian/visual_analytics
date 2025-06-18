import networkx as nx
import community.community_louvain as community_louvain
import plotly.graph_objects as go
from dash import dcc
from itertools import cycle


class KnowledgeGraphPlot:
    """
    Class to create and visualize a knowledge graph using Plotly and NetworkX.

    Attributes:
            data (dict): Graph data in node-link format.
            edge_types_available (list): List of unique edge types in the graph.
            color_map (dict): Mapping of edge types to colors.
            html_id (str): HTML id for the Dash graph component.
    """

    def __init__(self, data, html_id):
        """
        Initialize the KnowledgeGraphPlot instance.

        Args:
                data (dict): Graph data in node-link format.
                html_id (str): HTML id for the Dash graph component.
        """
        self.data = data
        self.edge_types_available = self._get_edge_types()
        self.color_map = self._generate_color_map()
        self.html_id = html_id

    def _get_edge_types(self):
        """
        Extract unique edge types from the graph data.

        Returns:
                list: Unique edge types found in the graph edges.
        """
        G = nx.node_link_graph(self.data, edges="links")
        return list({d.get("type") for _, _, d in G.edges(data=True)})

    def _generate_color_map(self):
        """
        Generate a mapping from edge types to colors.

        Returns:
                dict: Edge type as keys and color strings as values.
        """

        colors = cycle(["red", "green", "blue", "orange", "purple", "brown", "cyan", "magenta", "gray"])
        return {etype: next(colors) for etype in self.edge_types_available}

    def build_graph(self, selected_types):
        """
        Build a filtered undirected graph containing only edges of the selected types.

        Args:
                selected_types (list): List of edge types to include.

        Returns:
                networkx.Graph: Subgraph containing only the filtered edges.
        """
        G = nx.node_link_graph(self.data, edges="links").to_undirected()
        filtered_edges = [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if d.get("type") in selected_types]
        return G.edge_subgraph(filtered_edges).copy()

    def generate_figure(self, selected_types, highlight_node_id=None):
        """
        Generate a Plotly figure visualizing the graph filtered by edge types.

        Nodes are grouped by type with different shapes and colors.
        Communities are detected and nodes are colored by community.

        Args:
                selected_types (list): List of edge types to include in the visualization.
                highlight_node_id (optional): Node id to highlight (larger size and gold border).

        Returns:
                plotly.graph_objects.Figure: The generated figure object.
        """
        G_filtered = self.build_graph(selected_types)

        # Define marker shapes and colors for node types
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

        non_interactive_types = {"Entity.Person", "Entity.Location.Region", "Entity.Organization.GovernmentOrg"}

        # Group nodes by their type attribute
        nodes_by_type = {}
        for node, attrs in G_filtered.nodes(data=True):
            ctype = attrs.get("type", "Unknown")
            nodes_by_type.setdefault(ctype, []).append(node)

        if len(G_filtered.nodes) == 0:
            return go.Figure(layout={"title": "No edges match the selected types."})

        # Compute layout and detect communities
        pos = nx.spring_layout(G_filtered, seed=42)
        partition = community_louvain.best_partition(G_filtered)
        nx.set_node_attributes(G_filtered, partition, "community")

        # Create edge traces per edge type
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

        # Prepare a general node trace colored by community (used as fallback)
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
        )

        # Initialize figure with edges and community-colored nodes
        fig = go.Figure(data=edge_traces + [node_trace])
        fig.update_layout(
            title="CatchNet (Filtered by Edge Type)",
            title_font_size=16,
            showlegend=False,
            legend=dict(
                bgcolor="rgba(0,0,0,0)",  # transparent background
                bordercolor="rgba(0,0,0,0)",  # no border
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="white",
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )

        # Create separate node traces per type for shape and color customization
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
                        opacity=1,
                    ),
                    name=ctype,
                )
            )

        fig = go.Figure(data=edge_traces + node_traces)

        fig.update_layout(
            title="CatchNet (Filtered by Edge Type)",
            title_font_size=16,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)",
                font=dict(color="#083B6E"),
            ),
            paper_bgcolor="#001f3f",
            plot_bgcolor="#001f3f",
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
        )

        return fig

    def get_edge_type_options(self):
        """
        Get edge types formatted for use as options in UI controls (e.g., dropdowns).

        Returns:
                list of dict: Each dict contains 'label' and 'value' keys for an edge type.
        """
        return [{"label": etype, "value": etype} for etype in self.edge_types_available]

    def render(self):
        """
        Render the Dash Graph component with the knowledge graph figure.

        Initially shows all edge types.

        Returns:
                dash.dcc.Graph: Dash Graph component with the generated figure.
        """
        fig = self.generate_figure(self.edge_types_available)
        return dcc.Graph(id=self.html_id, figure=fig)
