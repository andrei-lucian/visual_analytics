from main import app
import nltk


def safe_nltk_download(resource_name):
    try:
        nltk.data.find(resource_name)
    except LookupError:
        nltk.download(resource_name.split("/")[-1])


# Usage:
safe_nltk_download("tokenizers/punkt")
safe_nltk_download("tokenizers/punkt_tab")
safe_nltk_download("sentiment/vader_lexicon")

import spacy

try:
    spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download

    download("en_core_web_sm")
    spacy.load("en_core_web_sm")

from widgets.layout import *
from callbacks.callbacks import register_callbacks

if __name__ == "__main__":

    """
    This is the main layout of the webpage, its children are then sub divided
    into further html layouts
    """
    app.layout = create_layout()
    register_callbacks(app)

    app.run(debug=True, dev_tools_ui=True)
