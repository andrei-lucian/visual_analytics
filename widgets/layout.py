# --- App Layout ---
from dash import html, dcc

from widgets.knowledge_graph import *
from widgets.horizontal_bar import *
from widgets.heatmap import *
from widgets.dropdown import *
from widgets.wordcloud import *
from widgets.stream_graph import *
from widgets.sentiment_comparison_bar import *

with open("data/mc1.json", "r") as f:
    data = json.load(f)

initial_point = "Namorna Transit Ltd"  # Company that all plots get initialized to

knowledge_graph = KnowledgeGraphPlot(data=data, html_id="graph")
horizontal_bar = HorizontalBarPlot(data=data, html_id="horizontalbar")
edge_type_dropdown = EdgeTypeDropdown(knowledge_graph._get_edge_types(), html_id="dropdown")
heatmap = Heatmap(data=data, html_id="heatmap")
wordcloud = WordCloudWidget([], id="wordcloud")
stream_graph = StreamGraph(data=data, html_id="stream_graph")


loading_cute_spinner = html.Div(className="cute-spinner", children=[html.Div(), html.Div(), html.Div()])


from dash import html, dcc


def create_layout():
    return html.Div(
        style={
            "width": "100vw",
            "height": "100vh",
            "display": "flex",
            "flexDirection": "column",
            "padding": "20px 40px",
            "boxSizing": "border-box",
            "gap": "15px",
            "alignItems": "center",
        },
        children=[
            # Top row: Knowledge Graph + Dropdown, Heatmap, Wordcloud with dcc.Loading
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "justifyContent": "space-between",
                    "height": "50%",
                    "width": "100%",
                    "gap": "10px",
                },
                children=[
                    # Knowledge Graph + Dropdown container
                    html.Div(
                        style={
                            "flex": 2,
                            "display": "flex",
                            "flexDirection": "column",
                            "border": "1px solid #ccc",
                            "borderRadius": "8px",
                            "padding": "10px",
                            "backgroundColor": "#fafafa",
                        },
                        children=[
                            html.Div(
                                edge_type_dropdown.render(),
                                style={
                                    "marginBottom": "8px",
                                    "alignSelf": "flex-start",
                                    "flex": 1,
                                },
                            ),
                            knowledge_graph.render(),
                        ],
                    ),
                    # Heatmap
                    html.Div(
                        heatmap.render(company_name=initial_point, clickData=None),
                        style={"flex": 1, "border": "1px solid #ccc", "borderRadius": "8px"},
                    ),
                    # Wordcloud container (outer div)
                    html.Div(
                        style={
                            "flex": 1,
                            "border": "1px solid #ccc",
                            # "borderRadius": "8px",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "color": "#001f3f",
                            "fontStyle": "italic",
                            "fontSize": "1.1rem",
                        },
                        children=[
                            dcc.Loading(
                                id="loading-wordcloud",
                                type="circle",
                                children=html.Div(
                                    id="wordcloud-container",
                                    children=[
                                        html.Div(
                                            "Click on the heatmap to load wordcloud",
                                            style={"marginBottom": "10px"},
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ],
            ),
            # Bottom row: Stream Graph, Horizontal Bar, Sentiment with dcc.Loading
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "justifyContent": "space-between",
                    "height": "40%",
                    "width": "100%",
                    "gap": "10px",
                },
                children=[
                    html.Div(
                        stream_graph.render(),
                        style={"flex": 2, "border": "1px solid #ccc", "borderRadius": "8px"},
                    ),
                    html.Div(
                        horizontal_bar.render(),
                        style={"flex": 1, "border": "1px solid #ccc", "borderRadius": "8px"},
                    ),
                    # Sentiment container (outer div)
                    html.Div(
                        style={
                            "flex": 1,
                            "border": "1px solid #ccc",
                            "borderRadius": "8px",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "color": "#001f3f",
                            "fontStyle": "italic",
                            "fontSize": "1.1rem",
                        },
                        children=[
                            dcc.Loading(
                                id="loading-sentiment",
                                type="circle",
                                children=html.Div(
                                    id="sentiment-container",
                                    children=[
                                        html.Div(
                                            "Click on the heatmap to load sentiment comparison",
                                            style={"marginBottom": "10px"},
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
