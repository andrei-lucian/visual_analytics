import nltk
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from dash import html

nltk.download("punkt")
nltk.download("vader_lexicon")


class SentimentHighlighter:
    def __init__(self, html_id):
        self.id = html_id
        self.sia = SentimentIntensityAnalyzer()

    def render(self):
        return html.Div(id=self.id, style={"whiteSpace": "pre-wrap", "lineHeight": "1.8"})

    def _highlight_sentence(self, sentence, score):
        if score > 0.3:
            color = "green"
        elif score < -0.3:
            color = "red"
        else:
            color = "gray"
        return html.Span(sentence + " ", style={"color": color})

    def get_highlighted_text(self, text, entities=None):
        sentences = sent_tokenize(text)
        if entities:
            sentences = [s for s in sentences if any(name in s for name in entities)]
        highlighted = []
        for s in sentences:
            score = self.sia.polarity_scores(s)["compound"]
            highlighted.append(self._highlight_sentence(s, score))
        return highlighted
