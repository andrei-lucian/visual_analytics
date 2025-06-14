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
)
from transformers.pipelines import AggregationStrategy
import numpy as np
from transformers import AutoTokenizer
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer


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

    def render(self):
        return html.Div(id=self.id)

    def generate_wordcloud(self, articles, entity):
        phrases_list = []
        for art in articles:
            path = f"data/articles/{art}.txt"
            with open(path, "r") as file:
                text = file.read()
                phrases = self.get_key_phrases(text, entity)
                for phrase in phrases:
                    phrases_list.append(phrase)
        phrases_list = phrases_list[:7]
        if not phrases_list:
            phrases_list = ["empty"]
        text = " ".join(phrase.replace(" ", "_") for phrase in phrases_list)

        wc = WordCloud(
            width=self.width,
            height=self.height,
            background_color=self.background_color,
        ).generate(text)

        buf = BytesIO()
        wc.to_image().save(buf, format="PNG")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode()
        image = f"data:image/png;base64,{encoded}"
        return html.Img(src=image, style={"maxWidth": "100%", "height": "auto"})

    def get_key_phrases(self, text, entity):
        model_name = "ml6team/keyphrase-extraction-distilbert-inspec"
        extractor = KeyphraseExtractionPipeline(model=model_name)

        # Split into sentences
        sentences = self.custom_sentence_split(text)

        # Filter sentences mentioning the company
        entity_sentences = [s for s in sentences if entity.lower() in s.lower()]

        text = " ".join(entity_sentences)

        model_phrases = extractor(text)
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
                polarity = sia.polarity_scores(text)["compound"]
                if polarity != 0:
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
