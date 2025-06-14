# --- App Layout ---
from dash import html

from widgets.knowledge_graph import *
from widgets.horizontal_bar import *
from widgets.heatmap import *
from widgets.dropdown import *
from widgets.wordcloud import *
from widgets.stream_graph import *
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
stream_graph = StreamGraph(data=data, html_id="stream_graph")


from dash import html, dcc


def create_layout():
    layout = html.Div(
        style={"display": "flex", "flexDirection": "row", "width": "100%", "height": "100%"},
        children=[
            # Left side (50%)
            html.Div(
                style={"width": "50%", "padding": "10px"},
                children=[
                    edge_type_dropdown.render(),
                    knowledge_graph.render(),
                    horizontal_bar.render(),
                    stream_graph.render(),
                ],
            ),
            # Right side (50%)
            html.Div(
                style={"width": "50%", "padding": "10px"},
                children=[
                    heatmap.render(company_name=initial_point, clickData=None),
                    # Wordcloud container with placeholder
                    dcc.Loading(
                        html.Div(
                            id="wordcloud-container",
                            children=[
                                # This placeholder text will be replaced by the actual wordcloud on callback
                                html.Div(
                                    "Click on the heatmap to load wordcloud",
                                    style={
                                        "height": "300px",  # adjust height to match your wordcloud widget
                                        "display": "flex",
                                        "justifyContent": "center",
                                        "alignItems": "center",
                                        "color": "#a8c7e7",  # light blueish text
                                        "fontStyle": "italic",
                                        # "backgroundColor": "#1a1f2b",  # dark background consistent with theme
                                        "borderRadius": "12px",
                                        "marginBottom": "20px",
                                    },
                                )
                            ],
                        ),
                    ),
                    # Sentiment container with placeholder
                    dcc.Loading(
                        html.Div(
                            id="sentiment-container",
                            children=[
                                html.Div(
                                    "Click on the heatmap to load sentiment comparison",
                                    style={
                                        "height": "200px",  # match your sentiment bar height
                                        "display": "flex",
                                        "justifyContent": "center",
                                        "alignItems": "center",
                                        "color": "#a8c7e7",
                                        "fontStyle": "italic",
                                        # "backgroundColor": "#1a1f2b",
                                        "borderRadius": "12px",
                                    },
                                )
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )
    return layout
