import json
import pandas as pd
import plotly.express as px
from dash import dcc, html


class Heatmap:
    def __init__(self, data, html_id):
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
        df_nodes = pd.DataFrame(self.data["nodes"])
        df_links = pd.DataFrame(self.data["links"])
        return df_nodes, df_links

    def _get_company_from_link(self, row):
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
        df = self.df_links

        df[["sentiment", "sentiment_recipient"]] = df["type"].apply(
            lambda x: pd.Series(self.event_sentiment_map.get(x, ("neutral", "target")))
        )

        df["company"] = df.apply(self._get_company_from_link, axis=1)
        df.dropna(subset=["company"], inplace=True)

        df["_date_added"] = pd.to_datetime(df["_date_added"], errors="coerce")
        df["month"] = df["_date_added"].dt.to_period("M")

        self.df_links = df

    def generate_figure(self, company_name):
        self.company_name = company_name
        df = self.df_links[self.df_links["company"] == self.company_name].dropna().copy()
        self.selected_articles = df["_articleid"]
        if df.empty:
            return px.imshow([[0]], title="No sentiment data available")

        df["score"] = df["sentiment"].map(self.sentiment_score_map)
        df["month"] = df["month"].astype(str)

        df_heat = df.groupby(["month", "_raw_source"])["score"].mean().reset_index()

        heatmap_data = df_heat.pivot(index="_raw_source", columns="month", values="score").fillna(0)

        fig = px.imshow(
            heatmap_data,
            zmin=-1,  # Set minimum value of color scale
            zmax=1,  # Set maximum value of color scale
            color_continuous_scale=[(0, "red"), (0.5, "white"), (1, "green")],
            aspect="auto",
            labels=dict(x="Month", y="News Source", color="Sentiment Score"),
            title=f"Sentiment Toward {self.company_name} Over Time (by Source)",
        )

        fig.update_xaxes(side="top")
        return fig

    def render(self, company_name):
        fig = self.generate_figure(company_name=company_name)
        return dcc.Graph(id=self.html_id, figure=fig)

    def get_article(self, month, source):
        # print(self.company_name, month, source)
        filtered = self.df_links[
            (self.df_links["company"] == self.company_name)
            & (self.df_links["month"] == month[:7])
            & (self.df_links["_raw_source"] == source)
        ]
        articles = list(set(filtered["_articleid"]))
        return articles
