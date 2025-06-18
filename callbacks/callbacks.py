from dash.dependencies import Input, Output
from widgets.layout import *
from widgets.sentiment_comparison_bar import *
from dash import Output, Input, callback_context, no_update


def register_callbacks(app):
    """
    Register all Dash callback functions for interactivity.

    This function connects the UI elements (graph, dropdown, heatmap, wordcloud, sentiment bars, etc.)
    with their corresponding logic using Dash callbacks. It enables dynamic behavior when users
    interact with the app, such as clicking on nodes in the graph or cells in the heatmap.

    Callbacks Registered:
    ---------------------
    1. update_graph:
            Updates the network graph visualization based on selected edge types and clicked node.

    2. update_heatmap:
            Updates the sentiment heatmap based on the node selected in the graph.

    3. update_all_outputs:
            Updates the word cloud, horizontal bar chart, stream graph, and sentiment comparison
            when a heatmap cell is clicked. Falls back to placeholder messages when only the graph is clicked.

    Parameters:
    -----------
    app : dash.Dash
            The Dash app instance to which callbacks are registered.

    Returns:
    --------
    None
    """

    @app.callback(Output("graph", "figure"), Input("dropdown", "value"), Input("graph", "clickData"))
    def update_graph(selected_edge_types, clicked_node_id):
        if not selected_edge_types:
            selected_edge_types = knowledge_graph.edge_types_available

        if clicked_node_id is not None:
            text = clicked_node_id["points"][0]["text"]
            text = text.split("Node: ")[1].split("<br>")[0]
        else:
            text = "Namorna Transit Ltd"

        return knowledge_graph.generate_figure(selected_edge_types, highlight_node_id=text)

    @app.callback(Output("heatmap", "figure"), Input("graph", "clickData"), prevent_initial_call=True)
    def update_heatmap(clickData):
        company_name = clickData["points"][0]["text"]
        company_name = company_name.split("Node: ")[1].split("<br>")[0]
        return heatmap.generate_figure(company_name, clickData)

    @app.callback(
        [
            Output("wordcloud-container", "children"),
            Output("horizontalbar", "figure"),
            Output("stream_graph", "figure"),
            Output("sentiment-container", "children"),
        ],
        [Input("heatmap", "clickData"), Input("graph", "clickData")],
        prevent_initial_call=True,
    )
    def update_all_outputs(heatmap_click, graph_click):
        triggered = callback_context.triggered[0]["prop_id"].split(".")[0]

        if triggered == "graph":
            company_name = graph_click["points"][0]["text"].split("Node: ")[1].split("<br>")[0]
            horizontal_bar._prepare_plot_df(company_name, None)
            stream_graph._prepare_plot_df(company_name, None)
            return (
                wordcloud.render_placeholder(),
                horizontal_bar.generate_figure(),
                stream_graph.generate_figure(),
                sentiment_bar.render_placeholder(),
            )

        if triggered == "heatmap" and heatmap_click is not None:
            point = heatmap_click["points"][0]
            month = point["x"]
            source = point["y"]
            source, month = heatmap.map_abbr_to_full(source, month)  # Pass abbreviation to full source and month
            # Get company name from last clicked node on graph
            if graph_click is not None:
                company_name = graph_click["points"][0]["text"].split("Node: ")[1].split("<br>")[0]
            else:
                company_name = "Namorna Transit Ltd"  # fallback

            articles = heatmap.get_articles(month, source)
            horizontal_bar._prepare_plot_df(company_name, heatmap_filter=(month, source))
            stream_graph._prepare_plot_df(company_name, heatmap_filter=(month, source))

            return (
                wordcloud.render_wordcloud(articles, company_name, month, source),
                horizontal_bar.generate_figure(month, source),
                stream_graph.generate_figure(month, source),
                sentiment_bar.render(heatmap.get_sentiment_score(heatmap_click), articles, company_name, month, source),
            )

        return no_update, no_update, no_update, no_update
