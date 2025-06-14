# --- App Layout ---
from dash import html

from widgets.knowledge_graph import *
from widgets.horizontal_bar import *
from widgets.heatmap import *
from widgets.dropdown import *
from widgets.wordcloud import *
from widgets.parallel_coordinate_plot import *
from widgets.sentiment_comparison_bar import *


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

with open("data/mc1.json", "r") as f:
    data = json.load(f)

initial_point = "Namorna Transit Ltd"  # Company that all plots get initialized to

knowledge_graph = KnowledgeGraphPlot(data=data, html_id="graph")
horizontal_bar = HorizontalBarPlot(data=data, html_id="horizontalbar")
edge_type_dropdown = EdgeTypeDropdown(knowledge_graph._get_edge_types(), html_id="dropdown")
heatmap = Heatmap(data=data, html_id="heatmap")
wordcloud = WordCloudWidget([], id="wordcloud")
parallel_coordinate = ParallelCoordinatePlot(data=data, html_id="stream_graph")


def create_layout():
    layout = html.Div(
        style={"display": "flex", "flexDirection": "row", "width": "100%", "height": "100%"},
        children=[
            # Left side (67%)
            html.Div(
                style={"width": "50%", "padding": "10px"},
                children=[
                    edge_type_dropdown.render(),
                    knowledge_graph.render(),
                    horizontal_bar.render(),
                    parallel_coordinate.render(),
                ],
            ),
            html.Div(
                style={"width": "50%", "padding": "10px"},
                children=[
                    heatmap.render(initial_point),
                    dcc.Loading(wordcloud.render()),
                    html.Div(id="sentiment-container"),
                ],
            ),
        ],
    )
    return layout
