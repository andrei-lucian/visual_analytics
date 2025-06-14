from main import app
import nltk

nltk.download("punkt")
nltk.download('punkt_tab')
nltk.download("vader_lexicon")

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
