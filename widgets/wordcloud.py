import base64
from io import BytesIO
from typing import List
from wordcloud import WordCloud
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


class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    def __init__(self, model, *args, **kwargs):
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
            *args,
            **kwargs,
        )

    def postprocess(self, all_outputs):
        results = super().postprocess(
            all_outputs=all_outputs,
            aggregation_strategy=AggregationStrategy.FIRST,
        )
        return np.unique([result.get("word").strip() for result in results])


class WordCloudWidget:
    def __init__(self, phrases: List[str], width=800, height=400, background_color="white", id=None):
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

    def render(self):
        return html.Div(id=self.id)

    def generate_wordcloud(self, articles, entity):
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
        phrases_with_sentiment = [(phrase, self.classify_sentiment(phrase, entity)) for phrase in unique_phrases]
        print(phrases_with_sentiment)
        return self.render_phrase_tags(phrases_with_sentiment)

    def classify_sentiment(self, text, entity):
        inputs = self.tokenizer(text, entity, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.polarity_model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)
        label_id = probs.argmax().item()
        labels = ["negative", "neutral", "positive"]
        score = probs[0][label_id].item()

        # Add sign to the score based on sentiment label
        if labels[label_id] == "negative":
            score = -score
        elif labels[label_id] == "neutral":
            score = 0.0

        return labels[label_id], score

    def sentiment_color(self, phrase, score):
        phrase_lower = phrase.lower()
        if phrase == "Phantom triplet! This company was never actually mentioned in the alleged article.":
            return "purple"
        elif any(keyword in phrase_lower for keyword in self.force_red_keywords) or score < -0.2:
            return "red"
        elif any(keyword in phrase_lower for keyword in self.force_green_keywords) or score > 0.2:
            return "green"
        elif any(keyword in phrase_lower for keyword in self.force_grey_keywords):
            return "gray"
        else:
            return "gray"

    def render_phrase_tags(self, phrases_with_sentiment):
        return html.Div(
            id=self.id or "phrase-tags",
            style={"display": "flex", "flexWrap": "wrap", "gap": "10px"},
            children=[
                html.Span(
                    phrase,
                    style={
                        "backgroundColor": self.sentiment_color(phrase, score),
                        "color": "white",
                        "padding": "6px 10px",
                        "borderRadius": "12px",
                        "fontWeight": "bold",
                        "fontSize": "16px",
                        "whiteSpace": "normal",  # allow multi-line
                        "overflow": "visible",  # no clipping
                        "textOverflow": "unset",  # disable ellipsis
                    },
                    title=f"Sentiment: {score:+.2f}",
                )
                for phrase, (label, score) in sorted(phrases_with_sentiment, key=lambda x: -abs(x[1][1]))
            ],
        )

    def get_key_phrases(self, text, entity):
        # Split into sentences
        sentences = self.custom_sentence_split(text)

        # Filter sentences mentioning the company
        entity_sentences = [s for s in sentences if entity.lower() in s.lower()]

        text = " ".join(entity_sentences)

        model_phrases = self.keyphrase_extractor(text)
        model_phrases = [str(s) for s in model_phrases.tolist()]
        nlp_phrases = self.extract_polar_chunks(text, entity)

        key_phrases = set(nlp_phrases + model_phrases)

        return key_phrases

    def extract_polar_chunks(self, text, entity):
        # Load spaCy model (small English model)
        nlp = spacy.load("en_core_web_sm")

        # Initialize VADER sentiment analyzer
        sia = SentimentIntensityAnalyzer()
        # Split into sentences
        sentences = self.custom_sentence_split(text)
        # Filter sentences mentioning the company
        entity_sentences = [s for s in sentences if entity.lower() in s.lower()]

        chunk_polarities = []

        for sent in entity_sentences:
            doc = nlp(sent)

            for chunk in doc.noun_chunks:
                text = chunk.text
                # Get polarity score (compound) for the chunk text
                # polarity = sia.polarity_scores(text)["compound"]
                # if polarity != 0:
                chunk_polarities.append(text)

        return chunk_polarities

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
