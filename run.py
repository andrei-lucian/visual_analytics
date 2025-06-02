from app.main import app
from app.load_df import *
from app.views.map import *
from app.views.dropdown import *
from app.views.barchart import *
from app.views.layout import *
from app.callbacks.callbacks import register_callbacks

from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import sys
import os


if __name__ == "__main__":

    """
    This is the main layout of the webpage, its children are then sub divided
    into further html layouts
    """

    app.layout = create_layout()
    register_callbacks(app)

    app.run(debug=True, dev_tools_ui=True)
