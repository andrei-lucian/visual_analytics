import plotly.express as px
from dash import dcc
import pandas as pd


class PCP:
    """
    A class to create a  PCP visualization of edge types categorized by sentiment
    and annotated by different users, based on graph data containing nodes and links.

    Attributes:
                    html_id (str): The HTML element ID for rendering the Dash Graph component.
                    data (dict): Dictionary containing 'nodes' and 'links' information.
                    edge_type_sentiment (dict): Mapping from edge types to sentiment categories.
                    df_nodes (pd.DataFrame): DataFrame constructed from nodes data.
                    df_links (pd.DataFrame): DataFrame constructed from links data.
                    edge_types_available (List[str]): Sorted list of edge types ordered by sentiment.
                    df_plot (pd.DataFrame): DataFrame used for plotting after processing.
                    fig (plotly.graph_objs.Figure): Plotly figure object for the  PCP.
    """

    def __init__(self, data, html_id):
        """
        Initializes the PCP instance by preparing dataframes, edge types,
        processed plotting data, and the initial figure.

        Parameters:
                        data (dict): Dictionary containing 'nodes' and 'links' lists.
                        html_id (str): The HTML id string for the Dash Graph component.
        """
        self.html_id = html_id
        self.data = data

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
        self._prepare_plot_df()
        self.fig = self.generate_figure()

    def _create_dfs(self):
        """
        Converts the input data dictionaries into pandas DataFrames for nodes and links.

        Returns:
                        Tuple[pd.DataFrame, pd.DataFrame]: DataFrames for nodes and links respectively.
        """
        nodes = self.data["nodes"]
        links = self.data["links"]
        return pd.DataFrame(nodes), pd.DataFrame(links)

    def _get_edge_types(self):
        """
        Retrieves unique edge types from links and sorts them according to sentiment priority:
        negative < neutral < positive.

        Returns:
                        List[str]: Sorted list of edge types based on their sentiment category.
        """
        types = self.df_links["type"].unique()
        sentiment_order = {"negative": 0, "neutral": 1, "positive": 2}
        return sorted(types, key=lambda x: sentiment_order.get(self.edge_type_sentiment.get(x, "neutral"), 1))

    def _prepare_plot_df(self, selected_point="Namorna Transit Ltd", heatmap_filter=None):
        """
        Prepares the DataFrame for plotting by filtering links related to a selected node,
        optionally applying a time and source filter, then aggregating counts of edge types
        by annotators.

        Parameters:
                        selected_point (str, optional): The node (source or target) to filter links by.
                                                                                                                                                        Defaults to "Namorna Transit Ltd".
                        heatmap_filter (Tuple[datetime-like, str], optional): Tuple containing a date filter
                                                                                                                                                        (year-month) and raw source string to further filter links.
                                                                                                                                                        Defaults to None.
        """
        if selected_point is not None:
            filtered_df = self.df_links[
                (self.df_links["source"] == selected_point) | (self.df_links["target"] == selected_point)
            ]

            if heatmap_filter is not None:
                # Ensure datetime column is parsed for filtering
                filtered_df = filtered_df.copy()
                filtered_df["_date_added"] = pd.to_datetime(filtered_df["_date_added"])

                filter_date = pd.to_datetime(heatmap_filter[0])
                filter_source = heatmap_filter[1]

                filtered_df = filtered_df[
                    (filtered_df["_date_added"].dt.year == filter_date.year)
                    & (filtered_df["_date_added"].dt.month == filter_date.month)
                    & (filtered_df["_raw_source"] == filter_source)
                ]
        else:
            filtered_df = self.df_links

        annotators = filtered_df["_last_edited_by"].dropna().unique()
        all_types = self.edge_types_available

        rows = []

        for annotator in annotators:
            subset = filtered_df[filtered_df["_last_edited_by"] == annotator]
            counts = subset["type"].value_counts()
            full_counts = {t: counts.get(t, 0) for t in all_types}
            full_counts["_last_edited_by"] = annotator
            rows.append(full_counts)

        if rows:
            df_wide = pd.DataFrame(rows)
            self.df_plot = df_wide.melt(id_vars="_last_edited_by", var_name="edge_type", value_name="count")
        else:
            # Create an empty DataFrame with expected columns
            self.df_plot = pd.DataFrame(columns=["_last_edited_by", "edge_type", "count"])

    def _add_sentiment_bands(self, fig):
        """
        Adds colored background bands to the plotly figure to visually indicate the sentiment
        category (positive, neutral, negative) associated with each edge type.

        Parameters:
                        fig (plotly.graph_objs.Figure): The Plotly figure to add sentiment bands to.
        """
        total_counts = (
            self.df_plot.groupby("edge_type")["count"].sum().reindex(self.edge_types_available).fillna(0).cumsum()
        )

        sentiment_colors = {"positive": "green", "neutral": "lightgray", "negative": "red"}

        # Clear previous shapes to avoid duplication
        shapes = []
        for i, edge_type in enumerate(self.edge_types_available):
            sentiment = self.edge_type_sentiment.get(edge_type, "neutral")
            color = sentiment_colors.get(sentiment, "lightgray")

            shapes.append(
                dict(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0=edge_type if i == 0 else self.edge_types_available[i - 1],
                    x1=edge_type,
                    y0=0,
                    y1=1,
                    fillcolor=color,
                    opacity=0.15,
                    layer="below",
                    line_width=0,
                )
            )
        fig.update_layout(shapes=shapes)

    def generate_figure(self, month="", source=""):
        """
        Generates the Plotly area chart figure representing the  PCP,
        with traces for each annotator and colored sentiment bands.

        Returns:
                        plotly.graph_objs.Figure: The generated  PCP figure.
        """
        df_melted = self.df_plot
        df_melted = df_melted.rename(columns={"_last_edited_by": "Annotator"})
        if month == "":
            title = "Edge Type  PCP by Annotator"
        else:
            title = f"Edge Type PCP by Annotator <br> (source: {source} ({month}))"
        fig = px.area(
            df_melted,
            x="edge_type",
            y="count",
            color="Annotator",
            category_orders={"edge_type": self.edge_types_available},
            title=title,
        )

        # Disable stacking by setting stackgroup=None for all traces
        for trace in fig.data:
            trace.update(stackgroup=None)

        fig.update_layout(
            xaxis=dict(
                tickangle=45,
                tickfont=dict(size=13, color="#083B6E"),
            ),
            yaxis=dict(
                tickfont=dict(color="#083B6E", size=13),
                title="Count",
            ),
            font=dict(color="#083B6E", size=16),
            legend_title=dict(font=dict(color="#083B6E")),
            paper_bgcolor="#B9D3F6",
            plot_bgcolor="white",
            title_x=0.5,
        )

        # Add colored background bands for sentiment categories
        self._add_sentiment_bands(fig)

        return fig

    def render(self):
        """
        Returns the Dash Graph component rendering the prepared figure.

        Returns:
                        dash.dcc.Graph: Dash Graph component for the  PCP visualization.
        """
        return dcc.Graph(id=self.html_id, figure=self.fig)
