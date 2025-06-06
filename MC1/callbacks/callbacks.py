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

    @app.callback(
        Output("wordcloud", "children"),
        Input("heatmap", "clickData"),
        prevent_initial_call=True,
    )
    def display_articles(clickData):
        if clickData:
            point = clickData["points"][0]
            month = point["x"]
            source = point["y"]
            print(f"Clicked heatmap cell: Month={month}, Source={source}")
            articles = heatmap.get_article(month, source)
            return wordcloud.generate_wordcloud(articles, heatmap.company_name)
