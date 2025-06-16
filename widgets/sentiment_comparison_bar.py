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

    def render(self, triplet_sentiment_score, articles, entity):
        """
        Renders the diverging bar chart wrapped in a styled Div.

        Returns:
                dash.html.Div: A styled Div containing the Dash Graph.
        """
        fig = self.build_figure(triplet_sentiment_score, articles, entity)
        return html.Div(
            dcc.Graph(id=self.html_id, figure=fig),
            style={
                "borderRadius": "8px",
                "color": "#001f3f",
                "fontStyle": "italic",
                "fontSize": "1.1rem",
                "margin": "0",
                "backgroundColor": "#B9D3F6",
                "flexShrink": 0,
                "flexGrow": 0,
                "display": "flex",
                "flexWrap": "wrap",
                "justifyContent": "flex-start",
                "alignItems": "flex-start",
                "gap": "6px",
                "padding": "12px 16px",  # spacing inside the box
            },
        )

    def build_figure(self, triplet_sentiment_score, articles, entity):
        """
        Constructs the Plotly Figure with a horizontal diverging bar chart
        showing sentiment scores for the extracted triplet and each article.

        Parameters:
                triplet_sentiment_score (float): The sentiment score of the extracted triplet.
                articles (List[str]): List of article filenames to analyze.
                entity (str): The entity/aspect to analyze sentiment for.

        Returns:
                plotly.graph_objects.Figure: The generated diverging bar chart figure.
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
            paper_bgcolor="#001f3f",
            plot_bgcolor="#001f3f",
            font=dict(color="#083B6E"),
        )

        return fig

    def classify_aspect_sentiment(self, articles, entity):
        """
        Performs aspect-based sentiment classification on sentences mentioning the entity
        in each article using a pretrained transformer model.

        Parameters:
                articles (List[str]): List of article filenames (without extension) to analyze.
                entity (str): The entity/aspect to analyze sentiment for.

        Returns:
                List[float]: List of sentiment scores for each article, in the same order as the input articles.
                                         Scores range from -1 (negative) to +1 (positive).
        """
        sentiments = []
        for art in articles:
            path = f"data/articles/{art}.txt"
            with open(path, "r") as file:
                text = file.read()
                # Split text into sentences
                sentences = self.custom_sentence_split(text)
                # Filter sentences mentioning the entity
                entity_sentences = " ".join([s for s in sentences if entity.lower() in s.lower()])

                model_name = "yangheng/deberta-v3-base-absa-v1.1"
                tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)

                # Tokenize the concatenated sentences with the aspect as text_pair
                inputs = tokenizer(entity_sentences, entity, return_tensors="pt")

                # Run model inference without gradient calculation
                with torch.no_grad():
                    outputs = model(**inputs)

                logits = outputs.logits
                probs = F.softmax(logits, dim=1)

                # Calculate sentiment score as weighted sum: negative, neutral, positive
                sentiment_score = -1 * probs[0][0] + 0 * probs[0][1] + 1 * probs[0][2]
                sentiments.append(sentiment_score.item())
        return sentiments

    def custom_sentence_split(self, text):
        """
        Splits the input text into sentences, first by paragraphs (double newlines),
        then by sentence boundaries using NLTK's sent_tokenize.

        Parameters:
                text (str): The text to split into sentences.

        Returns:
                List[str]: List of sentences extracted from the input text.
        """
        blocks = text.split("\n\n")
        sentences = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            sentences.extend(sent_tokenize(block))
        return sentences
