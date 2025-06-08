import nltk
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
import plotly.graph_objs as go
from dash import dcc
from dash import html


class SentimentBoxplot:
    def __init__(self, id):
        self.sia = SentimentIntensityAnalyzer()
        self.html_id = id

    def _compute_sentiment_scores(self, articles, entities):
        scores = []
        for art in articles:
            path = f"data/articles/{art}.txt"
            with open(path, "r") as file:
                text = file.read()
                sentences = sent_tokenize(text)
                entity_sentences = [s for s in sentences if any(name in s for name in entities)]
                sentiment_scores = [self.sia.polarity_scores(s)["compound"] for s in entity_sentences]
                if sentiment_scores:
                    score = sum(sentiment_scores) / len(sentiment_scores)
                else:
                    score = 0
                scores.append(score)
        print(scores)
        return scores

    def render(self, articles, entities):
        fig = self.get_boxplot_figure(articles, entities)
        return dcc.Graph(id=self.html_id, figure=fig)

    def get_boxplot_figure(self, articles, entities):
        scores = self._compute_sentiment_scores(articles, entities)
        fig = go.Figure(
            data=[
                go.Box(
                    y=scores,
                    boxpoints="all",
                    jitter=0.5,
                    pointpos=-1.8,
                    marker=dict(color="blue"),
                    name="Avg Sentiment",
                )
            ],
            layout=go.Layout(
                title="Average Sentiment Scores",
                yaxis=dict(title="Sentiment (-1 to 1)"),
                margin=dict(l=40, r=40, t=40, b=40),
                height=400,
            ),
        )
        return fig
