from dash.dependencies import Input, Output
from widgets.layout import *


def register_callbacks(app, knowledge_graph):
    @app.callback(Output("graph", "figure"), Input("dropdown", "value"))
    def update_graph(selected_edge_types):
        if not selected_edge_types:
            # If nothing selected, show empty or full graph
            selected_edge_types = knowledge_graph.edge_types_available

        fig = knowledge_graph.generate_figure(selected_edge_types)
        return fig
