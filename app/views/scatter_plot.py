import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dash import dcc, html
from utils.data_processing import *
import plotly.express as px


class ScatterPlot(html.Div):
    def __init__(self, df, name, x_col="pca_x", y_col="pca_y", color_col="Genre", height=400):
        self.df = df
        self.html_id = name.lower().replace(" ", "-") + "-scatter-plot"
        self.x_col = x_col
        self.y_col = y_col
        self.color_col = color_col

        color_map = px.colors.qualitative.Plotly
        colors = [color_map[i % len(color_map)] for i in range(len(unique_genres))]
        genre_color_dict = dict(zip(unique_genres, colors))
        point_colors = merged_df["PrimaryGenre"].map(genre_color_dict)

        figure = {
            "data": [
                {
                    "x": df[self.x_col],
                    "y": df[self.y_col],
                    "mode": "markers",
                    "marker": {"size": 12, "color": point_colors},
                    "type": "scatter",
                    "text": df["Title_x"],  # hover info
                    "hoverinfo": "text",
                }
            ],
            "layout": {
                "title": "Sample Scatter Plot",
                "xaxis": {"title": self.x_col},
                "yaxis": {"title": self.y_col},
                "height": height,
                "plot_bgcolor": "#26232C",
                "paper_bgcolor": "#26232C",
                "font": {"color": "white"},
            },
        }

        super().__init__(
            className="graph_card",
            style={
                "padding": "10px",
                "backgroundColor": "#26232C",
                "color": "white",
                "marginBottom": "15px",
            },
            children=[
                dcc.Graph(
                    id=self.html_id,
                    figure=figure,
                )
            ],
        )
