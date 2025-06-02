# --- App Layout ---
from flask import app
from dash import html

from app.main import app
from app.load_df import *
from app.views.map import *
from app.views.dropdown import *
from app.views.barchart import *
from app.views.scatter_plot import *
from app.views.range_slider import *
from app.views.stream_graph import *
from app.views.line_plot import *

from app.utils.data_processing import *

# --- Styles ---
sidebar_style = {
    "width": "20%",
    "backgroundColor": "#f0f0f0",
    "padding": "20px",
    "boxShadow": "2px 0px 5px rgba(0,0,0,0.1)",
}
scatter_style = {
    "width": "80%",
    "display": "flex",
    "flexDirection": "column",
    "height": "100vh",
    "overflow": "hidden",
}
center_style = {
    "width": "85%",
    "display": "flex",
    "flexDirection": "column",
    "padding": "10px",
}
bottom_content_style = {
    "marginTop": "20px",
    "backgroundColor": "#26232C",
    "color": "white",
    "padding": "15px",
    "height": "200px",
}
main_content_style = {
    "display": "flex",
    "flexDirection": "row",
    "height": "100vh",
}

# merged = full_df

# bar_chart = BarChartCard(
#     name="Top Polarizing Movies (by Rating Std Dev)",
#     df=merged,
#     x_col="RatingStd",
#     y_col="Title",
#     top_n=10,
# )
scatter_plot = ScatterPlot(df=merged_df, name="Scatter")
genre_dropdown = Dropdown("Genre Dropdown", unique_genres)
year_slider = YearRangeSlider(name="Year Slider", df=merged_df)
stream_graph = StreamGraph(genre_pivot)
line_plot = LinePlot(genre_year_avg_rating)

sidebar = html.Div(
    [
        html.H2("Controls"),
        html.Label("Choose a category"),
        genre_dropdown,
        html.Br(),
        html.Label("Adjust parameter"),
        year_slider,
    ]
)


def create_layout():
    layout = html.Div(
        style=main_content_style,
        children=[
            html.Div(style=sidebar_style, children=[sidebar]),
            html.Div(style=scatter_style, children=[scatter_plot, stream_graph, line_plot]),
        ],
    )
    return layout
