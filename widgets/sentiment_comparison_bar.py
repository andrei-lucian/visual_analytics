import plotly.graph_objects as go
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from dash import dcc, html
from nltk.tokenize import sent_tokenize


class DivergingSentimentPlot:
    """
    Class to generate a diverging bar chart comparing sentiment scores of multiple articles
    related to a specific entity, alongside an extracted triplet sentiment score.

    Sentiment scores are computed by applying aspect-based sentiment analysis
    on sentences mentioning the entity within each article.

    Attributes:
        html_id (str): The HTML id used to render the Dash Graph component.
    """

    def __init__(self, html_id):
        """
        Initializes the DivergingSentimentPlot instance.

        Parameters:
            html_id (str): The HTML element ID for the Dash Graph component.
        """
        self.html_id = html_id

    def render_placeholder(self):
        """
        Create a placeholder for the wordcloud widget.
        This is what is shown on startup and when no heatmap cell has been selected yet.
        """
        return html.Div(
            style={
                "height": "100%",
                "backgroundColor": "#B9D3F6",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "borderRadius": "8px",
            },
            children=[
                html.Div(
                    "Click on heatmap to load", style={"fontSize": "1.1rem", "fontStyle": "italic", "color": "#083B6E"}
                )
            ],
        )

    def render(self, triplet_sentiment_score, articles, entity, month, source):
        """
        Returns a Dash Graph with the sentiment diverging bar chart.

        Returns:
            dash.dcc.Graph: The Dash Graph.
        """
        fig = self.build_figure(triplet_sentiment_score, articles, entity, month, source)
        return dcc.Graph(
            id=self.html_id,
            figure=fig,
            config={"responsive": True},
            style={"width": "100%", "height": "100%"},
        )

    def build_figure(self, triplet_sentiment_score, articles, entity, month, source):
        """
        Builds a horizontal bar chart comparing triplet and article sentiment scores.

        Returns:
            Figure: The generated diverging bar chart figure.
        """
        sentiment_scores = self.classify_aspect_sentiment(articles, entity)
        sentiment_scores.insert(0, triplet_sentiment_score)
        y_labels = ["CatchNet"] + [f"Article {i}" for i in range(len(articles))]

        articles.insert(0, "Extracted triplet sentiment")
        colors = ["gray" if s is None else ("red" if s < 0 else "green") for s in sentiment_scores]
        text_labels = [f"{s:+.2f}" if s is not None else "N/A" for s in sentiment_scores]

        fig = go.Figure(
            go.Bar(
                x=sentiment_scores,
                y=y_labels,
                orientation="h",
                marker_color=colors,
                text=text_labels,
                textposition="auto",
                hovertext=articles,
                hoverinfo="text+x",
            )
        )
        fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="gray")

        fig.update_layout(
            title=dict(text=f"{source} ({month}) <br> vs CatchNet sentiment", x=0.5, xanchor="center"),
            xaxis_title="Sentiment Score",
            yaxis_title="Article",
            xaxis_range=[-1, 1],
            bargap=0.5,
            font=dict(color="#083B6E", size=9),
        )
        return fig

    def classify_aspect_sentiment(self, articles, entity):
        """
        Returns sentiment scores (-1 to 1) for each article regarding the entity.

        Returns:
            List[float]: Sentiment scores for each article.
        """
        sentiments = []
        for art in articles:
            path = f"data/articles/{art}.txt"
            with open(path, "r") as file:
                text = file.read()
                sentences = self.custom_sentence_split(text)
                entity_sentences = " ".join(s for s in sentences if entity.lower() in s.lower())

                model_name = "yangheng/deberta-v3-base-absa-v1.1"
                tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)

                inputs = tokenizer(entity_sentences, entity, return_tensors="pt")

                with torch.no_grad():
                    outputs = model(**inputs)

                probs = F.softmax(outputs.logits, dim=1)
                score = -1 * probs[0][0] + probs[0][2]
                sentiments.append(score.item())
        return sentiments

    def custom_sentence_split(self, text):
        """
        Splits text into sentences using paragraph and sentence tokenization.

        Returns:
            List[str]: List of extracted sentences.
        """
        blocks = text.split("\n\n")
        sentences = []
        for block in blocks:
            block = block.strip()
            if block:
                sentences.extend(sent_tokenize(block))
        return sentences
