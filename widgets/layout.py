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


def create_layout():
    return html.Div(
        style={
            "maxwidth": "100%",
            "maxheight": "100%",
            # "height": "100vh",
            "display": "flex",
            "flexDirection": "column",
            "padding": "20px 40px",
            "gap": "15px",
        },
        children=[
            # Top row: Heatmap, Knowledge Graph, Wordcloud+Sentiment
            html.Div(
                style={
                    "height": "50%",
                    "display": "flex",
                    "flexDirection": "row",
                    "gap": "15px",
                },
                children=[
                    # Heatmap (30%)
                    html.Div(
                        style={
                            "width": "30%",
                            "display": "flex",
                            "flexDirection": "column",
                            "backgroundColor": "#B9D3F6",
                            "borderRadius": "12px",  # <-- rounded corners here
                        },
                        children=[
                            html.Div(
                                heatmap.render(company_name=initial_point, clickData=None),
                                style={
                                    "flex": "1",
                                    "borderRadius": "8px",
                                    "padding": "0",
                                    "margin": "0",
                                    "backgroundColor": "#B9D3F6",
                                },
                            ),
                        ],
                    ),
                    # Knowledge Graph (40%)
                    html.Div(
                        style={
                            "width": "40%",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "10px",
                            "backgroundColor": "#B9D3F6",
                            "borderRadius": "12px",  # <-- rounded corners here
                        },
                        children=[
                            html.Div(edge_type_dropdown.render(), style={"height": "40px"}),
                            html.Div(
                                knowledge_graph.render(),
                                style={
                                    "flex": "1",
                                    "borderRadius": "12px",  # <-- rounded corners here
                                    "backgroundColor": "#B9D3F6",
                                    "padding": "0",
                                    "margin": "0",
                                },
                            ),
                        ],
                    ),
                    # Wordcloud + Sentiment (30%)
                    html.Div(
                        style={
                            "width": "30%",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "10px",
                        },
                        children=[
                            # Wordcloud
                            html.Div(
                                style={
                                    "flex": "1",
                                    "borderRadius": "8px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                    "color": "#001f3f",
                                    "fontStyle": "italic",
                                    "fontSize": "1.1rem",
                                    "padding": "0",
                                    "margin": "0",
                                    "backgroundColor": "#B9D3F6",
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
                            # Sentiment
                            html.Div(
                                style={
                                    "flex": "1",
                                    "borderRadius": "8px",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                    "color": "#001f3f",
                                    "fontStyle": "italic",
                                    "fontSize": "1.1rem",
                                    "padding": "10px",
                                    "margin": "0",
                                    "overflow": "auto",
                                    "boxSizing": "border-box",
                                    "backgroundColor": "#B9D3F6",
                                },
                                children=[
                                    dcc.Loading(
                                        id="loading-sentiment",
                                        type="circle",
                                        children=html.Div(
                                            id="sentiment-container",
                                            style={"flex": "1", "width": "100%", "height": "100%"},
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
            ),
            # Bottom row: Stream Graph + Horizontal Bar
            html.Div(
                style={
                    "height": "50%",
                    "display": "flex",
                    "flexDirection": "row",
                    "gap": "15px",
                },
                children=[
                    # Horizontal Bar (50%)
                    html.Div(
                        horizontal_bar.render(),
                        style={
                            "width": "50%",
                            "borderRadius": "8px",
                            "padding": "0",
                            "margin": "0",
                            "backgroundColor": "#B9D3F6",
                            "borderRadius": "12px",  # <-- rounded corners here
                        },
                    ),
                    # Stream Graph (50%)
                    html.Div(
                        stream_graph.render(),
                        style={
                            "width": "50%",
                            "borderRadius": "8px",
                            "padding": "0",
                            "margin": "0",
                            "backgroundColor": "#B9D3F6",
                            "borderRadius": "12px",  # <-- rounded corners here
                        },
                    ),
                ],
            ),
        ],
    )
