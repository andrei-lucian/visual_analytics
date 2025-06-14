from dash.dependencies import Input, Output
from widgets.layout import *
from widgets.sentiment_comparison_bar import *
from dash import Output, Input, callback_context, no_update


def register_callbacks(app):
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
            placeholder_style = {
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "color": "#a8c7e7",
                "fontStyle": "italic",
                "backgroundColor": "#1a1f2b",
                "borderRadius": "12px",
            }

            return (
                html.Div(
                    "Click on the heatmap to load wordcloud",
                    style={**placeholder_style, "height": "300px", "marginBottom": "20px"},
                ),
                no_update,
                no_update,
                html.Div(
                    "Click on the heatmap to load sentiment comparison",
                    style={**placeholder_style, "height": "200px"},
                ),
            )

        if triggered == "heatmap" and heatmap_click is not None:
            point = heatmap_click["points"][0]
            month = point["x"]
            source = point["y"]

            # Get company name from last clicked node on graph
            if graph_click is not None:
                company_name = graph_click["points"][0]["text"].split("Node: ")[1].split("<br>")[0]
            else:
                company_name = "Namorna Transit Ltd"  # fallback

            articles = heatmap.get_articles(month, source)

            wordcloud_component = wordcloud.generate_wordcloud(articles, company_name)
            horizontal_bar._prepare_plot_df(company_name, heatmap_filter=(month, source))
            stream_graph._prepare_plot_df(company_name, heatmap_filter=(month, source))

            sentiment_bar = DivergingSentimentPlot(html_id="sentiment-container")
            sentiment_figure = dcc.Graph(
                figure=sentiment_bar.build_figure(heatmap.get_sentiment_score(heatmap_click), articles, company_name)
            )

            return (
                wordcloud_component,
                horizontal_bar.generate_figure(),
                stream_graph.generate_figure(),
                sentiment_figure,
            )

        return no_update, no_update, no_update, no_update
