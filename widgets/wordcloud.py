from typing import List
from dash import html
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import (
    TokenClassificationPipeline,
    AutoModelForTokenClassification,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
from transformers.pipelines import AggregationStrategy
import numpy as np
from transformers import AutoTokenizer
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
import torch
import torch.nn.functional as F
import random


class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    """
    Custom pipeline for keyphrase extraction using a token classification model.

    Extends the Hugging Face TokenClassificationPipeline and applies
    first-token aggregation strategy to extract unique keyphrases from text.
    """

    def __init__(self, model, *args, **kwargs):
        """
        Initializes the pipeline with a pretrained model and tokenizer.

        Parameters:
            model (str): The model name or path to load.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
            *args,
            **kwargs,
        )

    def postprocess(self, all_outputs):
        """
        Postprocesses the raw token classification outputs.

        Applies aggregation strategy and returns unique keyphrases.

        Parameters:
            all_outputs (List): Raw model outputs from token classification.

        Returns:
            np.ndarray: Array of unique extracted keyphrases as strings.
        """
        results = super().postprocess(
            all_outputs=all_outputs,
            aggregation_strategy=AggregationStrategy.FIRST,
        )
        return np.unique([result.get("word").strip() for result in results])


class WordCloudWidget:
    """
    Generates a word cloud-like Dash component with keyphrases colored by sentiment.

    Keyphrases are extracted from articles with respect to a target entity,
    classified for sentiment, and displayed with color-coded styles.
    """

    def __init__(self, phrases: List[str], width=800, height=400, background_color="white", id=None):
        """
        Initializes the word cloud widget.

        Loads models for keyphrase extraction and phrase-level sentiment classification.

        Parameters:
            phrases (List[str]): List of phrases (not directly used, can be for future).
            width (int): Width of the word cloud display area.
            height (int): Height of the word cloud display area.
            background_color (str): Background color for the widget container.
            id (str, optional): HTML element ID for the widget.
        """
        self.phrases = phrases
        self.width = width
        self.height = height
        self.background_color = background_color
        self.id = id
        self.phrase_polarity_model_name = "yangheng/deberta-v3-base-absa-v1.1"
        self.tokenizer = AutoTokenizer.from_pretrained(self.phrase_polarity_model_name, use_fast=False)
        self.polarity_model = AutoModelForSequenceClassification.from_pretrained(self.phrase_polarity_model_name)
        self.keyphrase_extractor_model_name = "ml6team/keyphrase-extraction-distilbert-inspec"
        self.keyphrase_extractor = KeyphraseExtractionPipeline(model=self.keyphrase_extractor_model_name)
        self.force_red_keywords = {"overfishing, condemnation"}
        self.force_green_keywords = {"sustainab"}
        self.force_grey_keywords = {"stichtingmarine"}
        self.nlp = spacy.load("en_core_web_sm")

    def generate_wordcloud(self, articles, entity):
        """
        Extracts keyphrases from articles related to an entity, classifies their sentiment,
        and returns a Dash HTML Div with color-coded phrases.

        Parameters:
            articles (List[str]): List of article filenames (without extension).
            entity (str): The entity name to focus extraction and sentiment on.

        Returns:
            dash.html.Div: Dash Div component containing color-coded keyphrase tags.
        """
        phrases_list = []
        for art in articles:
            path = f"data/articles/{art}.txt"
            with open(path, "r") as file:
                text = file.read()
                phrases = self.get_key_phrases(text, entity)
                phrases_list.extend(phrases)

        if not phrases_list:
            phrases_list = ["Phantom triplet! This company was never actually mentioned in the alleged article."]

        # Compute sentiment for each unique phrase
        unique_phrases = list(set(phrases_list))

        phrases_with_sentiment = []
        for phrase in unique_phrases:
            label, score = self.classify_sentiment(phrase, entity)
            if label != "neutral":  # Filter out neutral phrases
                phrases_with_sentiment.append((phrase, (label, score)))

        if not phrases_with_sentiment:
            phrases_with_sentiment = [("All phrases were neutral", ("neutral", 0.0))]

        return self.render_phrase_tags(phrases_with_sentiment)

    def classify_sentiment(self, text, entity):
        """
        Classifies sentiment of a given phrase with respect to an entity using a pretrained model.

        Parameters:
            text (str): The phrase or text snippet to classify.
            entity (str): The entity to use as the aspect for sentiment classification.

        Returns:
            Tuple[str, float]: Sentiment label ("negative", "neutral", or "positive") and sentiment score.
                              Score is negative for negative sentiment, zero for neutral, and positive for positive.
        """
        inputs = self.tokenizer(text, entity, return_tensors="pt")
        with torch.no_grad():
            outputs = self.polarity_model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)
        label_id = probs.argmax().item()
        labels = ["negative", "neutral", "positive"]
        score = probs[0][label_id].item()

        if labels[label_id] == "negative":
            score = -score
        elif labels[label_id] == "neutral":
            score = 0.0

        return labels[label_id], score

    def sentiment_color(self, phrase, score):
        """
        Determines the display color for a phrase based on sentiment score and forced keyword rules.

        Parameters:
            phrase (str): The phrase text.
            score (float): The sentiment score of the phrase.

        Returns:
            str: CSS color hex.
        """
        phrase_lower = phrase.lower()
        if phrase == "Phantom triplet! This company was never actually mentioned in the alleged article.":
            return "#81d4fa"  # light blue
        elif any(keyword in phrase_lower for keyword in self.force_red_keywords) or score < -0.2:
            return "#e57373"  # softer red
        elif any(keyword in phrase_lower for keyword in self.force_green_keywords) or score > 0.2:
            return "#81c784"  # softer green
        elif any(keyword in phrase_lower for keyword in self.force_grey_keywords):
            return "#b0bec5"  # softer grey
        else:
            return "#b0bec5"  # softer grey fallback

    def render_phrase_tags(self, phrases_with_sentiment):
        """
        Create a nicer looking Dash Div with wordcloud-style spans.
        Font size and color depend on sentiment score.
        Positions get slight random shifts for organic distribution.
        """
        # Parameters for font size scaling
        min_font_size = 12
        max_font_size = 48

        # Normalize scores to 0-1 magnitude for sizing
        scores = [abs(score) for _, (_, score) in phrases_with_sentiment]
        max_score = max(scores) if scores else 1.0

        def font_size(score):
            # Linear scale score magnitude to font size range
            norm = abs(score) / max_score if max_score > 0 else 0
            size = min_font_size + norm * (max_font_size - min_font_size)
            return f"{int(size)}px"

        def random_shift():
            # Small random pixel shift for position jitter
            return f"translate({random.randint(-10, 10)}px, {random.randint(-10, 10)}px)"

        min_font = 14
        max_font = 32

        scores = [abs(score) for _, (_, score) in phrases_with_sentiment]
        max_score = max(scores) if scores else 1.0

        def font_size(score):
            norm = abs(score) / max_score if max_score > 0 else 0
            size = min_font + norm * (max_font - min_font)
            return f"{int(size)}px"

        return html.Div(
            id=self.id or "phrase-tags",
            style={
                "borderRadius": "8px",
                "color": "#001f3f",
                "fontStyle": "italic",
                "fontSize": "1.1rem",
                "padding": "0",
                "margin": "0",
                "backgroundColor": "#B9D3F6",
                "flexShrink": 0,
                "flexGrow": 0,
                "display": "flex",
                "flexWrap": "wrap",
                "justifyContent": "flex-start",
                "alignItems": "flex-start",
                "gap": "6px",
                "padding": "10px",
            },
            children=[
                html.Span(
                    phrase,
                    style={
                        "backgroundColor": self.sentiment_color(phrase, score),
                        "color": "white",
                        "padding": "4px 8px",  # smaller padding to make boxes smaller
                        "borderRadius": "12px",
                        "fontWeight": "bold",
                        "fontSize": "14px",  # slightly smaller text
                        "whiteSpace": "normal",
                        "overflow": "visible",
                        "textOverflow": "unset",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "textAlign": "center",  # center text horizontally
                        "minWidth": "60px",  # minimum width to keep boxes uniform
                        "maxWidth": "150px",  # max width to prevent overly large boxes
                        "wordBreak": "break-word",  # wrap long words
                    },
                    title=f"Sentiment: {score:+.2f}",
                    key=phrase,
                )
                for phrase, (label, score) in sorted(phrases_with_sentiment, key=lambda x: -abs(x[1][1]))
            ],
        )

    def get_key_phrases(self, text, entity):
        """
        Extracts keyphrases from text related to a given entity by combining model-based and
        NLP-based phrase extraction.

        Parameters:
            text (str): The article or text content.
            entity (str): The entity name to focus extraction on.

        Returns:
            Set[str]: A set of unique keyphrases related to the entity.
        """
        sentences = self.custom_sentence_split(text)
        entity_sentences = [s for s in sentences if entity.lower() in s.lower()]
        text = " ".join(entity_sentences)

        model_phrases = self.keyphrase_extractor(text)
        model_phrases = [str(s) for s in model_phrases.tolist()]
        nlp_phrases = self.extract_polar_chunks(text, entity)

        key_phrases = set(nlp_phrases + model_phrases)
        return key_phrases

    def extract_polar_chunks(self, text, entity):
        """
        Extracts noun chunks from sentences mentioning the entity.

        Parameters:
            text (str): Text to analyze.
            entity (str): The target entity.

        Returns:
            List[str]: List of noun chunk strings.
        """
        sentences = self.custom_sentence_split(text)
        entity_sentences = [s for s in sentences if entity.lower() in s.lower()]

        chunks = []
        for sent in entity_sentences:
            doc = self.nlp(sent)
            for chunk in doc.noun_chunks:
                chunks.append(chunk.text)

        return chunks

    def custom_sentence_split(self, text):
        """
        Splits text into sentences by first breaking into blocks (paragraphs),
        then splitting each block into sentences.

        Parameters:
            text (str): Text to split.

        Returns:
            List[str]: List of sentence strings.
        """
        blocks = text.split("\n\n")
        sentences = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            sentences.extend(sent_tokenize(block))
        return sentences
