# --- App Layout ---
from dash import html

from widgets.knowledge_graph import *
from widgets.parallel_coordinates import *
from widgets.heatmap import *
from widgets.dropdown import *

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

with open('data/mc1.json', "r") as f:
	data = json.load(f)

initial_point = 'Namorna Transit Ltd' # Company that all plots get initialized to

knowledge_graph = KnowledgeGraphPlot(data=data, html_id="graph")
parallel_coordinates = ParallelCoordinatesPlot(data=data, html_id="pcp")
edge_type_dropdown = EdgeTypeDropdown(knowledge_graph._get_edge_types(), html_id="dropdown")
heatmap = Heatmap(data=data, html_id="heatmap")

def create_layout():
    layout = html.Div(
        style={"display": "flex", "flexDirection": "row", "width": "100%", "height": "100%"},
        children=[
            # Left side (67%)
            html.Div(
                style={"width": "67%", "padding": "10px"},
                children=[
                    edge_type_dropdown.render(),
                    knowledge_graph.render(),
                    parallel_coordinates.render(),
                ],
            ),
            # Right side (33%) for heatmap
            html.Div(
                style={"width": "33%", "padding": "10px"},
                children=[
                    heatmap.render(initial_point),
                ],
            ),
        ],
    )
    return layout
