import plotly.express as px
from dash import dcc
import pandas as pd


class StreamGraph:
    def __init__(self, data, html_id):
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
        nodes = self.data["nodes"]
        links = self.data["links"]
        return pd.DataFrame(nodes), pd.DataFrame(links)

    def _get_edge_types(self):
        types = self.df_links["type"].unique()
        sentiment_order = {"negative": 0, "neutral": 1, "positive": 2}
        return sorted(types, key=lambda x: sentiment_order.get(self.edge_type_sentiment.get(x, "neutral"), 1))

    def _prepare_plot_df(self, selected_point="Namorna Transit Ltd", heatmap_filter=None):
        if selected_point is not None:
            filtered_df = self.df_links[
                (self.df_links["source"] == selected_point) | (self.df_links["target"] == selected_point)
            ]

            if heatmap_filter is not None:
                print(heatmap_filter)
                # Ensure your datetime column is parsed
                filtered_df["_date_added"] = pd.to_datetime(filtered_df["_date_added"])

                # Extract year and month
                filter_date = pd.to_datetime(heatmap_filter[0])
                filter_source = heatmap_filter[1]

                # Filter by month and source
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

        df_wide = pd.DataFrame(rows)
        self.df_plot = df_wide.melt(id_vars="_last_edited_by", var_name="edge_type", value_name="count")

    def _add_sentiment_bands(self, fig):
        # Calculate the cumulative counts for each edge_type across all annotators
        # This will define y-axis ranges for the bands
        total_counts = (
            self.df_plot.groupby("edge_type")["count"].sum().reindex(self.edge_types_available).fillna(0).cumsum()
        )

        sentiment_colors = {"positive": "green", "neutral": "lightgray", "negative": "red"}
        y0 = 0

        for i, edge_type in enumerate(self.edge_types_available):
            y1 = total_counts[edge_type]

            sentiment = self.edge_type_sentiment.get(edge_type, "neutral")
            color = sentiment_colors.get(sentiment, "lightgray")

            fig.add_shape(
                type="rect",
                xref="x",
                yref="y",
                x0=edge_type,
                x1=edge_type,
                y0=0,
                y1=y1,
                fillcolor=color,
                opacity=0.15,
                layer="below",
                line_width=0,
            )
            # Because x-axis is categorical, rectangles can't cover area horizontally by x0,x1.
            # Instead, we add rectangle over full vertical height at that x-position by using paper coords:
            # We'll fix this in the next step below.

        # Instead, add wider rectangles spanning full y height but limited x range (between edge types)
        # Convert categories to numerical x positions (0,1,2,...)
        x_positions = {et: i for i, et in enumerate(self.edge_types_available)}
        shapes = []
        for i, edge_type in enumerate(self.edge_types_available):
            sentiment = self.edge_type_sentiment.get(edge_type, "neutral")
            color = sentiment_colors.get(sentiment, "lightgray")

            # x-range: center at i, span from i - 0.5 to i + 0.5
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

        # Clear any previous shapes to avoid duplicates and add these shapes
        fig.update_layout(shapes=shapes)

    def generate_figure(self):
        df_melted = self.df_plot
        fig = px.area(
            df_melted,
            x="edge_type",
            y="count",
            color="_last_edited_by",
            category_orders={"edge_type": self.edge_types_available},
            title="Edge Type Stream Graph by Annotator",
        )

        fig.update_layout(
            xaxis=dict(
                tickangle=45,
                tickfont=dict(size=12),
            ),
            yaxis_title="Count",
            legend_title="Annotator",
        )

        # Add colored background bands for sentiment
        self._add_sentiment_bands(fig)

        return fig

    def render(self):
        return dcc.Graph(id=self.html_id, figure=self.fig)
