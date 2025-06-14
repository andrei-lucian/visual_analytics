from main import app
import nltk

nltk.download("punkt")
nltk.download('punkt_tab')
nltk.download("vader_lexicon")

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
