from main import app
import nltk
from widgets.layout import *
from callbacks.callbacks import register_callbacks

if __name__ == "__main__":

    """
    This is the main layout of the webpage, its children are then sub divided
    into further html layouts
    """
    # nltk.download("punkt")
    # nltk.download("vader_lexicon")

    app.layout = create_layout()
    register_callbacks(app)

    app.run(debug=True, dev_tools_ui=True)
