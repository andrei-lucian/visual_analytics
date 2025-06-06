from dash.dependencies import Input, Output
from widgets.layout import *


def register_callbacks(app):
    @app.callback(Output("graph", "figure"), Input("dropdown", "value"))
    def update_graph(selected_edge_types):
        if not selected_edge_types:
            # If nothing selected, show empty or full graph
            selected_edge_types = knowledge_graph.edge_types_available

        fig = knowledge_graph.generate_figure(selected_edge_types)
        return fig

    @app.callback(Output("pcp", "figure"), Input("graph", "clickData"), prevent_initial_call=True)
    def update_pcp(selected_point):
        text = selected_point["points"][0]["text"]
        text = text.split("Node: ")[1].split("<br>")[0]
        parallel_coordinates._prepare_plot_df(text)
        return parallel_coordinates.generate_figure()

    @app.callback(Output("heatmap", "figure"), Input("graph", "clickData"), prevent_initial_call=True)
    def update_heatmap(company_name):
        company_name = company_name["points"][0]["text"]
        company_name = company_name.split("Node: ")[1].split("<br>")[0]
        return heatmap.generate_figure(company_name)
