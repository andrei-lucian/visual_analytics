from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from dash import html

class SentimentHighlighter:
    """
    A class to analyze and highlight sentences in text based on their sentiment polarity scores.

    Sentences are colored green for positive sentiment, red for negative, and gray for neutral.
    Optionally, sentences can be filtered by the presence of specific entities.
    """

    def __init__(self, html_id):
        """
        Initializes the SentimentHighlighter with a Dash HTML container ID and
        sets up the VADER sentiment intensity analyzer.

        Parameters:
            html_id (str): The HTML element ID for the container where highlighted text will be rendered.
        """
        self.id = html_id
        self.sia = SentimentIntensityAnalyzer()

    def render(self):
        """
        Creates a Dash HTML Div component configured to display the highlighted text.

        Returns:
            dash.html.Div: A Div element with styles to preserve whitespace and line height.
        """
        return html.Div(id=self.id, style={"whiteSpace": "pre-wrap", "lineHeight": "1.8"})

    def _highlight_sentence(self, sentence, score):
        """
        Returns a Dash HTML Span element wrapping a sentence, styled by sentiment score.

        Sentences with compound scores above 0.3 are colored green,
        below -0.3 are red, and others are gray.

        Parameters:
            sentence (str): The sentence text to highlight.
            score (float): The compound sentiment score for the sentence.

        Returns:
            dash.html.Span: A Span element containing the sentence with appropriate color styling.
        """
        if score > 0.3:
            color = "green"
        elif score < -0.3:
            color = "red"
        else:
            color = "gray"
        return html.Span(sentence + " ", style={"color": color})

    def get_highlighted_text(self, text, entities=None):
        """
        Processes the input text, optionally filters sentences by entities, computes sentiment,
        and returns a list of styled Span elements for rendering.

        Parameters:
            text (str): The full text to analyze.
            entities (List[str], optional): List of entity strings to filter sentences.
                                            Only sentences containing any of these entities will be included.
                                            Defaults to None (include all sentences).

        Returns:
            List[dash.html.Span]: List of Span elements with sentences highlighted by sentiment.
        """
        sentences = sent_tokenize(text)
        if entities:
            sentences = [s for s in sentences if any(name in s for name in entities)]
        highlighted = []
        for s in sentences:
            score = self.sia.polarity_scores(s)["compound"]
            highlighted.append(self._highlight_sentence(s, score))
        return highlighted
