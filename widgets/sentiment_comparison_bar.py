import plotly.graph_objects as go
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from dash import dcc
from nltk.tokenize import sent_tokenize


class DivergingSentimentPlot:
    def __init__(self, html_id):
        """
        Initializes the plot with article titles and sentiment scores.

        Parameters:
        - article_titles (List[str]): Names or labels of the articles.
        - sentiment_scores (List[float]): Corresponding sentiment scores (-1 to 1).
        """
        self.html_id = html_id

    def render(self, triplet_sentiment_score, articles, entity):
        """
        Renders the diverging bar chart as a Dash Graph component.
        """
        fig = self.build_figure(triplet_sentiment_score, articles, entity)
        return dcc.Graph(id=self.html_id, figure=fig)

    def build_figure(self, triplet_sentiment_score, articles, entity):
        """
        Builds and returns a Plotly Figure with a diverging bar chart.
        """
        sentiment_scores = self.classify_aspect_sentiment(articles, entity)
        sentiment_scores.insert(0, triplet_sentiment_score)
        articles.insert(0, "Extracted triplet sentiment")
        colors = ["gray" if score is None else ("red" if score < 0 else "green") for score in sentiment_scores]
        text_labels = [f"{score:+.2f}" if score is not None else "N/A" for score in sentiment_scores]

        fig = go.Figure(
            go.Bar(
                x=sentiment_scores,
                y=articles,
                orientation="h",
                marker_color=colors,
                text=text_labels,
                textposition="outside",
            )
        )

        fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="gray")

        fig.update_layout(
            title="Sentiment Comparison of Articles",
            xaxis_title="Sentiment Score",
            yaxis_title="Article",
            xaxis_range=[-1, 1],
            bargap=0.5,
            plot_bgcolor="white",
            height=400 + 30 * len(articles),
        )

        return fig

    def classify_aspect_sentiment(self, articles, entity):
        sentiments = []
        for art in articles:
            path = f"data/articles/{art}.txt"
            with open(path, "r") as file:
                text = file.read()
                # Split into sentences
                sentences = self.custom_sentence_split(text)
                # Filter sentences mentioning the company
                entity_sentences = " ".join([s for s in sentences if entity.lower() in s.lower()])
                model_name = "yangheng/deberta-v3-base-absa-v1.1"
                tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)

                model = AutoModelForSequenceClassification.from_pretrained(model_name)

                # Tokenize the sentence with the aspect as text_pair
                inputs = tokenizer(entity_sentences, entity, return_tensors="pt", truncation=True)
                # Run the model
                with torch.no_grad():
                    outputs = model(**inputs)

                # Get logits and softmax probabilities
                logits = outputs.logits
                probs = F.softmax(logits, dim=1)
                sentiment_score = (
                    -1 * probs[0][0] + 0 * probs[0][1] + +1 * probs[0][2]  # negative  # neutral  # positive
                )
                sentiments.append(sentiment_score.item())
        return sentiments

    def custom_sentence_split(self, text):
        # Split text into blocks using double newlines (titles/paragraphs)
        blocks = text.split("\n\n")

        sentences = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            # Further split using sent_tokenize for real sentence boundaries
            sentences.extend(sent_tokenize(block))

        return sentences
