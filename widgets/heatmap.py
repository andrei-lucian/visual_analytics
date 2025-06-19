import pandas as pd
import plotly.express as px
from dash import dcc
import plotly.graph_objects as go
import numpy as np


class Heatmap:
    def __init__(self, data, html_id):
        """
        Initialize Heatmap with graph data and HTML component ID.
        """
        self.html_id = html_id

        self.company_types = {
            "Entity.Organization.FishingCompany",
            "Entity.Organization.Company",
            "Entity.Organization.LogisticsCompany",
            "Entity.Organization.NGO",
            "Entity.Organization",
            "Entity.Organization.GovernmentOrg",
        }

        self.sentiment_score_map = {"negative": -1, "neutral": 0, "positive": 1}
        self.data = data
        self.df_nodes, self.df_links = self._create_dfs()
        self.valid_companies = set(self.df_nodes[self.df_nodes["type"].isin(self.company_types)]["id"])
        self.selected_articles = None
        self.row_mapping = None
        self.col_mapping = None

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
        """
        Convert raw node and link data into DataFrames.
        """
        df_nodes = pd.DataFrame(self.data["nodes"])
        df_links = pd.DataFrame(self.data["links"])
        return df_nodes, df_links

    def _get_company_from_link(self, row):
        """
        Determine company involved in the link from source/target and recipient role.
        """
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
        """
        Enrich links with sentiment and company data, convert dates, and extract month.
        """
        df = self.df_links
        df[["sentiment", "sentiment_recipient"]] = df["type"].apply(
            lambda x: pd.Series(self.event_sentiment_map.get(x, ("neutral", "target")))
        )
        df["company"] = df.apply(self._get_company_from_link, axis=1)
        df.dropna(subset=["company"], inplace=True)
        df["_date_added"] = pd.to_datetime(df["_date_added"], errors="coerce")
        df["month"] = df["_date_added"].dt.to_period("M")
        self.df_links = df

    def generate_figure(self, company_name, clickData=None):
        """
        Create a heatmap figure showing sentiment over time for a company.
        """
        self.company_name = company_name
        df = self.df_links[self.df_links["company"] == self.company_name].dropna().copy()
        self.selected_articles = df["_articleid"]

        if df.empty:
            return px.imshow([[0]], title="No sentiment data available")

        df["score"] = df["sentiment"].map(self.sentiment_score_map)
        df["month"] = df["month"].astype(str)

        fixed_months = pd.period_range(start="2035-02", end="2035-07", freq="M").astype(str)
        df_heat = df.groupby(["month", "_raw_source"])["score"].mean().reset_index()
        heatmap_data = df_heat.pivot(index="_raw_source", columns="month", values="score")
        heatmap_data = heatmap_data.reindex(columns=fixed_months, fill_value=np.nan)

        original_cols = heatmap_data.columns
        heatmap_data.columns = pd.to_datetime(heatmap_data.columns).strftime("%b")
        self.col_mapping = dict(zip(heatmap_data.columns, original_cols))

        original_index = heatmap_data.index
        abbreviated_index = heatmap_data.index.to_series().apply(
            lambda name: ".".join([word[0] for word in name.split()])
        )
        self.row_mapping = {abbr: name for abbr, name in zip(abbreviated_index, original_index)}
        heatmap_data.index = abbreviated_index
        heatmap_data.index.name = "Source"

        fig = px.imshow(
            heatmap_data,
            zmin=-1,
            zmax=1,
            color_continuous_scale=[[0.0, "red"], [0.5, "white"], [1.0, "green"]],
            aspect="auto",
        )

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

        fig.update_layout(
            coloraxis_colorbar=dict(
                thickness=10,
                tickfont=dict(size=10),
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.2,
            ),
            margin=dict(t=85, l=0, r=0),
            paper_bgcolor="#B9D3F6",
            plot_bgcolor="white",
            xaxis=dict(tickangle=0, color="#083B6E", tickfont=dict(color="#083B6E", size=14)),
            yaxis=dict(color="#083B6E", tickfont=dict(color="#083B6E", size=14), tickangle=90),
            title=dict(
                text=f"Sentiment Toward {self.company_name}<br>Over Time (extracted from CatchNet)",
                x=0.5,
                y=0.95,
                xanchor="center",
                font=dict(size=15),
            ),
            font=dict(color="#083B6E", size=12),
        )

        fig.add_annotation(
            text="Sentiment",
            x=0.5,
            y=-0.17,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=12, color="#083B6E"),
            xanchor="center",
            yanchor="top",
        )

        fig.update_traces(z=heatmap_data.to_numpy())

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

        fig.update_xaxes(side="bottom", showgrid=True, gridcolor="lightgray", tickangle=0)
        fig.update_yaxes(showgrid=True, gridcolor="lightgray")

        return fig

    def render(self, company_name, clickData=None):
        """
        Render the heatmap as a Dash Graph component.
        """
        fig = self.generate_figure(company_name, clickData)
        return dcc.Graph(id=self.html_id, figure=fig)

    def get_articles(self, month, source):
        """
        Return article IDs for the selected company, month, and source.
        """
        filtered = self.df_links[
            (self.df_links["company"] == self.company_name)
            & (self.df_links["month"] == month[:7])
            & (self.df_links["_raw_source"] == source)
        ]
        return list(set(filtered["_articleid"]))

    def map_abbr_to_full(self, source_abbr, month_abbr):
        """
        Map abbreviated labels back to full source and month.
        """
        full_source = self.row_mapping.get(source_abbr)
        full_month = self.col_mapping.get(month_abbr)
        return full_source, full_month

    def get_sentiment_score(self, clickData):
        """
        Return sentiment score of a clicked heatmap cell, or None.
        """
        if not clickData:
            return None
        try:
            point = clickData["points"][0]
            raw_month = point["x"]
            source = point["y"]
            source, raw_month = self.map_abbr_to_full(source, raw_month)
            match = self.df_links[
                (self.df_links["company"] == self.company_name)
                & (self.df_links["month"].astype(str) == raw_month)
                & (self.df_links["_raw_source"] == source)
            ]
            if match.empty:
                return None
            return round(match["score"].mean(), 2)
        except Exception:
            return None
