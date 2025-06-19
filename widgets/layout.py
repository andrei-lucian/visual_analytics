# --- App Layout ---
from dash import html, dcc

from widgets.knowledge_graph import *
from widgets.horizontal_bar import *
from widgets.heatmap import *
from widgets.dropdown import *
from widgets.wordcloud import *
from widgets.pcp import *
from widgets.sentiment_comparison_bar import *

with open("data/mc1.json", "r") as f:
    data = json.load(f)

initial_point = "Namorna Transit Ltd"  # Company that all plots get initialized to

knowledge_graph = KnowledgeGraphPlot(data=data, html_id="graph")
horizontal_bar = HorizontalBarPlot(data=data, html_id="horizontalbar")
edge_type_dropdown = EdgeTypeDropdown(knowledge_graph._get_edge_types(), html_id="dropdown")
heatmap = Heatmap(data=data, html_id="heatmap")
wordcloud = WordCloudWidget([], id="wordcloud")
sentiment_bar = DivergingSentimentPlot("sentiment-bar")
stream_graph = PCP(data=data, html_id="stream_graph")


def create_layout():
    return html.Div(
        style={
            "maxwidth": "100%",
            "maxheight": "100%",
            "display": "flex",
            "flexDirection": "column",
            "padding": "20px",
            "gap": "15px",
        },
        children=[
            # Top row: Heatmap, Knowledge Graph, Wordcloud+Sentiment
            html.Div(
                style={
                    "height": "60vh",
                    "overflow": "hidden",
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
                            "borderRadius": "12px",
                        },
                        children=[
                            html.Div(
                                heatmap.render(company_name=initial_point, clickData=None),
                                style={"width": "100%", "height": "100%"},
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
                            "borderRadius": "12px",
                        },
                        children=[
                            html.Div(edge_type_dropdown.render(), style={"height": "40px"}),
                            html.Div(
                                knowledge_graph.render(),
                                style={
                                    "flex": "1",
                                    "borderRadius": "12px",
                                    "backgroundColor": "#B9D3F6",
                                    "padding": "0",
                                    "margin": "0",
                                    "overflow": "auto",
                                },
                            ),
                        ],
                    ),
                    # Wordcloud + Sentiment (30%)
                    html.Div(
                        style={
                            "width": "30%",
                            "height": "60vh",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "10px",
                            "flex": "1",
                        },
                        children=[
                            html.Div(
                                id="wordcloud-container",
                                style={
                                    "height": "calc(50% - 5px)",  # Account for half of the 10px gap
                                    "backgroundColor": "#B9D3F6",
                                    "borderRadius": "8px",
                                },
                                children=wordcloud.render_placeholder(),
                            ),
                            html.Div(
                                id="sentiment-container",
                                style={
                                    "height": "calc(50% - 5px)",  # Same here
                                    "backgroundColor": "#B9D3F6",
                                    "borderRadius": "8px",
                                },
                                children=sentiment_bar.render_placeholder(),
                            ),
                        ],
                    ),
                ],
            ),
            # Bottom row: Stream Graph + Horizontal Bar
            html.Div(
                style={
                    "height": "40vh",
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
                            "borderRadius": "12px",
                            "overflow": "auto",
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
                            "borderRadius": "12px",
                            "overflow": "auto",
                        },
                    ),
                ],
            ),
        ],
    )
