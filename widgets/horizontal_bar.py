import json
import pandas as pd
import plotly.graph_objects as go
from dash import dcc


class HorizontalBarPlot:
    """
    A class to create a horizontal bar chart comparing edge type frequencies between
    two algorithms: BassLine and ShadGPT.

    Attributes:
    -----------
    data : dict
                    Input graph data containing 'nodes' and 'links'.
    html_id : str
                    The ID for the Dash component.
    edge_type_sentiment : dict
                    Mapping of edge types to sentiment categories.
    df_nodes : pd.DataFrame
                    DataFrame containing node data.
    df_links : pd.DataFrame
                    DataFrame containing link (edge) data.
    edge_types_available : list
                    Sorted list of all unique edge types based on sentiment order.
    color_map : dict
                    Maps algorithm names to color codes.
    df_plot : pd.DataFrame
                    Prepared DataFrame for plotting.
    fig : plotly.graph_objects.Figure
                    The plotly figure generated.
    """

    def __init__(self, data, html_id):
        self.html_id = html_id
        self.data = data

        # Mapping edge types to sentiment categories
        self.edge_type_sentiment = {
            "Event.Applaud": "positive",
            "Event.Aid": "positive",
            "Event.Invest": "positive",
            "Event.Fishing.SustainableFishing": "positive",
            "Event.Criticize": "negative",
            "Event.Convicted": "negative",
            "Event.CertificateIssued.Summons": "negative",
            "Event.Fishing.OverFishing": "negative",
            "Event.CertificateIssued": "neutral",
            "Event.Transaction": "neutral",
            "Event.Fishing": "neutral",
            "Event.Owns.PartiallyOwns": "neutral",
            "Event.Communication.Conference": "neutral",
        }

        self.df_nodes, self.df_links = self._create_dfs()
        self.edge_types_available = self._get_edge_types()
        self.color_map = self._generate_color_map()
        self._prepare_plot_df(None)
        self.fig = self.generate_figure()

    def _create_dfs(self):
        """Create DataFrames from raw node/link JSON structures."""
        nodes = self.data["nodes"]
        links = self.data["links"]
        return pd.DataFrame(nodes), pd.DataFrame(links)

    def _get_edge_types(self):
        """Get unique edge types sorted by sentiment (neg → neu → pos)."""
        types = self.df_links["type"].unique()
        sentiment_order = {"negative": 0, "neutral": 1, "positive": 2}
        return sorted(types, key=lambda x: sentiment_order.get(self.edge_type_sentiment.get(x, "neutral"), 1))

    def _generate_color_map(self):
        """Assign numeric codes to algorithms for color mapping."""
        return {"BassLine": 0, "ShadGPT": 1}

    def _counts_to_full_dict(self, counts, all_types):
        """Ensure all edge types are present in count dictionary."""
        return {t: counts.get(t, 0) for t in all_types}

    def _prepare_plot_df(self, selected_point=None, heatmap_filter=None):
        """
        Prepare the plot DataFrame based on selection and optional filter.

        Parameters:
        -----------
        selected_point : str or None
                        The node selected from the graph.
        heatmap_filter : tuple(str, str) or None
                        A (month, source) tuple for additional filtering.
        """
        if selected_point is None:
            # Default to root company if nothing selected
            filtered_df = self.df_links[
                (self.df_links["source"] == "Namorna Transit Ltd") | (self.df_links["target"] == "Namorna Transit Ltd")
            ]
        else:
            filtered_df = self.df_links[
                (self.df_links["source"] == selected_point) | (self.df_links["target"] == selected_point)
            ]

            # Apply date/source filtering if heatmap clicked
            if heatmap_filter is not None:
                filtered_df = filtered_df.copy()
                filtered_df["_date_added"] = pd.to_datetime(filtered_df["_date_added"])

                filter_date = pd.to_datetime(heatmap_filter[0])
                filter_source = heatmap_filter[1]

                filtered_df = filtered_df[
                    (filtered_df["_date_added"].dt.year == filter_date.year)
                    & (filtered_df["_date_added"].dt.month == filter_date.month)
                    & (filtered_df["_raw_source"] == filter_source)
                ]

        # Split by algorithm
        df_baseline = filtered_df[filtered_df["_algorithm"] == "BassLine"]
        df_shadgpt = filtered_df[filtered_df["_algorithm"] == "ShadGPT"]

        all_types = self.edge_types_available

        # Count edge types
        counts_baseline = df_baseline["type"].value_counts()
        counts_shadgpt = df_shadgpt["type"].value_counts()

        # Normalize counts to include all types
        counts_baseline_full = self._counts_to_full_dict(counts_baseline, all_types)
        counts_shadgpt_full = self._counts_to_full_dict(counts_shadgpt, all_types)

        # Combine into DataFrame for plotting
        df_plot = pd.DataFrame([counts_baseline_full, counts_shadgpt_full])
        df_plot["_algorithm"] = ["BassLine", "ShadGPT"]
        df_plot["_algorithm_code"] = df_plot["_algorithm"].map(self.color_map)

        self.df_plot = df_plot

    def generate_figure(self, month="", source=""):
        """
        Create the vertical bar plot comparing edge type counts.

        Returns:
        --------
        fig : plotly.graph_objects.Figure
                        The constructed Plotly figure object.
        """
        fig = go.Figure()

        # Define bar colors
        colors = {"BassLine": "blue", "ShadGPT": "orange"}

        # Plot bars for each algorithm
        for alg in ["BassLine", "ShadGPT"]:
            df_alg = self.df_plot[self.df_plot["_algorithm"] == alg]
            fig.add_trace(
                go.Bar(
                    x=self.edge_types_available,
                    y=df_alg[self.edge_types_available].values.flatten(),
                    name=alg,
                    orientation="v",  # vertical bars
                    marker_color=colors.get(alg, "gray"),
                )
            )

        # Add colored background bands for sentiment categories on x-axis
        shapes = []
        x_labels = list(self.edge_types_available)
        sentiment_groups = {"negative": "red", "neutral": "white", "positive": "green"}
        x_index = {label: i for i, label in enumerate(x_labels)}
        current_group = None
        start = None

        for i, label in enumerate(x_labels + [None]):  # sentinel for final group
            sentiment = self.edge_type_sentiment.get(label, "neutral") if label else None
            if sentiment != current_group:
                if current_group is not None:
                    x0 = x_index[x_labels[start]] - 0.5
                    x1 = x_index[x_labels[i - 1]] + 0.5
                    shapes.append(
                        dict(
                            type="rect",
                            xref="x",
                            yref="paper",
                            y0=0,
                            y1=1,
                            x0=x0,
                            x1=x1,
                            fillcolor=sentiment_groups[current_group],
                            opacity=0.2,
                            layer="below",
                            line_width=0,
                        )
                    )
                current_group = sentiment
                start = i

        if month == "":
            title = "Edge Type Counts by Algorithm"
        else:
            title = f"Edge Type Counts by Algorithm <br> (source: {source} ({month}))"

        fig.update_layout(
            barmode="group",
            title=title,
            xaxis_title="Edge Type",
            yaxis_title="Count",
            legend_title="Algorithm",
            shapes=shapes,
            xaxis=dict(
                tickfont=dict(size=13, color="#083B6E"),
            ),
            yaxis=dict(
                tickfont=dict(color="#083B6E", size=13),
                title="Count",
            ),
            font=dict(color="#083B6E", size=16),
            paper_bgcolor="#B9D3F6",
            plot_bgcolor="white",
            title_x=0.5,
        )
        return fig

    def render(self):
        """
        Return the Dash component to render the bar chart.

        Returns:
        --------
        dcc.Graph
                        The graph component for Dash layout.
        """
        return dcc.Graph(id=self.html_id, figure=self.fig)
