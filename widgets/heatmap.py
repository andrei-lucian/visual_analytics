import pandas as pd
import plotly.express as px
from dash import dcc
import plotly.graph_objects as go
import numpy as np


class Heatmap:
    def __init__(self, data, html_id):
        """
        Initialize the Heatmap component.

        Parameters:
        - data (dict): Dictionary containing 'nodes' and 'links' for graph data.
        - html_id (str): HTML ID for Dash component.
        """
        self.html_id = html_id

        # Define valid company types
        self.company_types = {
            "Entity.Organization.FishingCompany",
            "Entity.Organization.Company",
            "Entity.Organization.LogisticsCompany",
            "Entity.Organization.NGO",
            "Entity.Organization",
            "Entity.Organization.GovernmentOrg",
        }

        # Map sentiment labels to numerical scores
        self.sentiment_score_map = {"negative": -1, "neutral": 0, "positive": 1}
        self.data = data
        self.df_nodes, self.df_links = self._create_dfs()
        self.valid_companies = set(self.df_nodes[self.df_nodes["type"].isin(self.company_types)]["id"])
        self.selected_articles = None

        # Map event types to sentiment and recipient
        self.event_sentiment_map = {
            "Event.Applaud": ("positive", "target"),
            "Event.Aid": ("positive", "target"),
            "Event.Invest": ("positive", "target"),
            "Event.Criticize": ("negative", "target"),
            "Event.Convicted": ("negative", "target"),
            "Event.CertificateIssued.Summons": ("negative", "target"),
            "Event.Fishing.OverFishing": ("negative", "target"),
            "Event.CertificateIssued": ("neutral", "target"),
            "Event.Transaction": ("neutral", "target"),
            "Event.Fishing": ("neutral", "target"),
            "Event.Owns.PartiallyOwns": ("neutral", "target"),
            "Event.Communication.Conference": ("neutral", "source"),
            "Event.Fishing.SustainableFishing": ("positive", "source"),
        }

        self._prepare_links()

    def _create_dfs(self):
        """Convert input node/link data to pandas DataFrames."""
        df_nodes = pd.DataFrame(self.data["nodes"])
        df_links = pd.DataFrame(self.data["links"])
        return df_nodes, df_links

    def _get_company_from_link(self, row):
        """Determine the company involved in a link based on recipient and node type."""
        target = row["target"]
        source = row["source"]
        recipient = row["sentiment_recipient"]
        if recipient == "target" and target in self.valid_companies:
            return target
        elif recipient == "source" and source in self.valid_companies:
            return source
        elif target in self.valid_companies:
            return target
        elif source in self.valid_companies:
            return source
        return None

    def _prepare_links(self):
        """Process links DataFrame to assign sentiment and associated company."""
        df = self.df_links

        # Assign sentiment and recipient type
        df[["sentiment", "sentiment_recipient"]] = df["type"].apply(
            lambda x: pd.Series(self.event_sentiment_map.get(x, ("neutral", "target")))
        )

        # Assign associated company
        df["company"] = df.apply(self._get_company_from_link, axis=1)
        df.dropna(subset=["company"], inplace=True)

        # Convert date and extract month
        df["_date_added"] = pd.to_datetime(df["_date_added"], errors="coerce")
        df["month"] = df["_date_added"].dt.to_period("M")

        self.df_links = df

    def generate_figure(self, company_name, clickData=None):
        """
        Generate the heatmap figure for a selected company.

        Parameters:
        - company_name (str): The selected company.
        - clickData (dict or None): Optional click data from Dash.

        Returns:
        - fig (plotly.graph_objects.Figure): The resulting heatmap.
        """
        self.company_name = company_name
        df = self.df_links[self.df_links["company"] == self.company_name].dropna().copy()
        self.selected_articles = df["_articleid"]

        if df.empty:
            return px.imshow([[0]], title="No sentiment data available")

        # Map sentiment to numeric score
        df["score"] = df["sentiment"].map(self.sentiment_score_map)
        df["month"] = df["month"].astype(str)

        # Step 1: Define fixed month range (update to match your dataset as needed)
        fixed_months = pd.period_range(start="2035-02", end="2035-07", freq="M").astype(str)

        # Step 2: Group and pivot as before
        df_heat = df.groupby(["month", "_raw_source"])["score"].mean().reset_index()
        heatmap_data = df_heat.pivot(index="_raw_source", columns="month", values="score")

        # Step 3: Reindex columns to match fixed month range
        heatmap_data = heatmap_data.reindex(columns=fixed_months, fill_value=np.nan)

        highlight_x = highlight_y = None
        if clickData:
            try:
                point = clickData["points"][0]
                highlight_x = point["x"][:7]  # normalize month
                highlight_y = point["y"]
            except Exception as e:
                print("Error extracting highlight coordinates:", e)
        if highlight_x and highlight_y:
            fig.add_shape(
                type="rect",
                xref="x",
                yref="y",
                x0=highlight_x,
                x1=highlight_x,
                y0=highlight_y,
                y1=highlight_y,
                line=dict(color="black", width=3),
            )

        fig = px.imshow(
            heatmap_data,
            zmin=-1,
            zmax=1,
            color_continuous_scale=[[0.0, "red"], [0.5, "white"], [1.0, "green"]],
            aspect="auto",
            labels=dict(x="Month", y="News Source", color="Sentiment Score"),
        )

        # Update heatmap trace
        fig.update_traces(
            hovertemplate="Score: %{z}<extra></extra>",
            zauto=False,
            zsmooth=False,
            xgap=2,
            ygap=2,
            showscale=True,
            hoverongaps=False,
            autocolorscale=False,
        )

        # Layout customization
        fig.update_layout(
            coloraxis_colorbar=dict(title="Sentiment"),
            margin=dict(t=100),
            paper_bgcolor="#B9D3F6",
            plot_bgcolor="white",
            xaxis=dict(tickangle=0, color="#083B6E", tickfont=dict(color="#083B6E", size=14)),
            yaxis=dict(
                color="#083B6E",
                tickfont=dict(color="#083B6E", size=14),
            ),
            title=dict(
                text=f"Sentiment Toward {self.company_name} Over Time <br>"
                "(by Source, extracted from triplet database)",  # your title text (can have <br> for line breaks)
                x=0.5,  # center horizontally (0 = left, 1 = right)
                xanchor="center",  # anchor the title center on that x position
                font=dict(size=20),  # optional: adjust font size
            ),
            font=dict(color="#083B6E", size=16),
        )
        fig.update_traces(
            z=heatmap_data.to_numpy(),
            colorscale=[[0, "red"], [0.5, "white"], [1, "green"]],
            zmin=-1,
            zmax=1,
        )
        fig.add_trace(
            go.Heatmap(
                z=heatmap_data.isna().astype(int),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                showscale=False,
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "lightgrey"]],
                hoverinfo="skip",
                xgap=2,
                ygap=2,
            )
        )

        fig.update_xaxes(side="top", showgrid=True, gridcolor="lightgray", tickangle=0)
        fig.update_yaxes(showgrid=True, gridcolor="lightgray")

        return fig

    def render(self, company_name, clickData=None):
        """
        Render the heatmap as a Dash Graph component.

        Parameters:
        - company_name (str): Company to display data for.
        - clickData (dict or None): Optional clickData for highlighting.

        Returns:
        - dcc.Graph: Dash component with the heatmap figure.
        """
        fig = self.generate_figure(company_name=company_name, clickData=clickData)
        return dcc.Graph(id=self.html_id, figure=fig)

    def get_articles(self, month, source):
        """
        Return a list of article IDs for the given month and news source.

        Parameters:
        - month (str): Month in 'YYYY-MM' format.
        - source (str): News source string.

        Returns:
        - list: Unique article IDs.
        """
        filtered = self.df_links[
            (self.df_links["company"] == self.company_name)
            & (self.df_links["month"] == month[:7])
            & (self.df_links["_raw_source"] == source)
        ]
        articles = list(set(filtered["_articleid"]))
        return articles

    def get_sentiment_score(self, clickData):
        """
        Given clickData from the heatmap, returns the sentiment score of that cell.
        Returns None if invalid or missing.

        Parameters:
        - clickData (dict or None): Click event data from the Dash graph.

        Returns:
        - float or None: Sentiment score (rounded) or None.
        """
        if not clickData:
            return None

        try:
            point = clickData["points"][0]
            raw_month = point["x"]
            source = str(point["y"])

            if isinstance(raw_month, str):
                month = raw_month[:7]  # assume format "YYYY-MM-DD" or "YYYY-MM"
            elif hasattr(raw_month, "strftime"):  # datetime or Timestamp
                month = raw_month.strftime("%Y-%m")
            else:
                month = str(raw_month)[:7]

        except (KeyError, IndexError, TypeError) as e:
            print("Error parsing clickData:", e)
            return None

        df = self.df_links[self.df_links["company"] == self.company_name].copy()
        df["score"] = df["sentiment"].map(self.sentiment_score_map)
        df["month"] = df["month"].dt.to_timestamp().dt.strftime("%Y-%m")
        df["_raw_source"] = df["_raw_source"].astype(str)

        df_heat = df.groupby(["month", "_raw_source"])["score"].mean().reset_index()
        heatmap_data = df_heat.pivot(index="_raw_source", columns="month", values="score")

        try:
            score = heatmap_data.loc[source, month]
            return None if pd.isna(score) else round(score, 3)
        except KeyError as e:
            print(f"Lookup failed. Source: '{source}', Month: '{month}' not found.")
            return None
