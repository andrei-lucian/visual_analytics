import base64
from io import BytesIO
from typing import List

from wordcloud import WordCloud
from dash import html
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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
                phrases = self.extract_entity_related_phrases(text, entity)
                for phrase in phrases:
                    phrases_list.append(phrase)
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

    def contains_polar_word(self, phrase):
        analyzer = SentimentIntensityAnalyzer()
        lexicon = analyzer.lexicon
        words = phrase.lower().split()
        return any(word in lexicon for word in words)

    def clean_text(self, text):
        return " ".join(text.strip().split())

    def phrase_mentions_entity(self, phrase, entity_name):
        entity_name = entity_name.lower()
        phrase = phrase.lower()
        entity_tokens = entity_name.split()
        return any(token in phrase for token in entity_tokens)

    def extract_entity_related_phrases(self, text, entity_name):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        phrases = set()

        for sent in doc.sents:
            sent_text = self.clean_text(sent.text)
            sent_doc = nlp(sent_text)

            # Proceed only if entity mentioned in sentence
            if entity_name.lower() not in sent_text.lower():
                continue

            # Extract noun chunks mentioning the entity or containing sentiment words
            for chunk in sent_doc.noun_chunks:
                chunk_text = self.clean_text(chunk.text)
                if (
                    self.phrase_mentions_entity(chunk_text, entity_name) or self.contains_polar_word(chunk_text)
                ) and 2 <= len(chunk_text.split()) <= 10:
                    phrases.add(chunk_text)

            # Extract verb phrases with entity as subject/object and polar words
            for token in sent_doc:
                if token.pos_ in ("VERB", "AUX") and self.contains_polar_word(token.text):
                    subjects = [child for child in token.children if child.dep_ in ("nsubj", "nsubjpass")]
                    objects = [child for child in token.children if child.dep_ in ("dobj", "obj")]

                    subject_related = any(self.phrase_mentions_entity(sub.text, entity_name) for sub in subjects)
                    object_related = any(self.phrase_mentions_entity(obj.text, entity_name) for obj in objects)

                    if subject_related or object_related:
                        phrase_tokens = [token]
                        for child in token.children:
                            if child.dep_ in ("dobj", "prep", "xcomp", "acomp"):
                                phrase_tokens.extend(list(child.subtree))
                        phrase_tokens = sorted(set(phrase_tokens), key=lambda t: t.i)
                        phrase_text = self.clean_text(" ".join([t.text for t in phrase_tokens]))
                        if 2 <= len(phrase_text.split()) <= 12:
                            phrases.add(phrase_text)

        return list(phrases)
