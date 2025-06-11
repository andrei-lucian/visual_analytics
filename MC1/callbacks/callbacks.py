from dash.dependencies import Input, Output
from widgets.layout import *
import re

def register_callbacks(app):	
	@app.callback(
		Output("graph", "figure"),
		Input("dropdown", "value"),
		Input("graph", "clickData")
	)
	def update_graph(selected_edge_types, clicked_node_id):
		if not selected_edge_types:
			selected_edge_types = knowledge_graph.edge_types_available

		if clicked_node_id is not None:
			text = clicked_node_id["points"][0]["text"]
			text = text.split("Node: ")[1].split("<br>")[0]
		else:
			text = "Namorna Transit Ltd"

		return knowledge_graph.generate_figure(
			selected_edge_types, highlight_node_id=text
		)

	@app.callback(Output("horizontalbar", "figure"), Input("graph", "clickData"), prevent_initial_call=True)
	def update_horizontalbar(selected_point):
		text = selected_point["points"][0]["text"]
		text = text.split("Node: ")[1].split("<br>")[0]
		horizontal_bar._prepare_plot_df(text)
		return horizontal_bar.generate_figure()
	
	@app.callback(
		Output("pcp", "figure"), 
		Input("graph", "clickData"), 
		prevent_initial_call=True
	)
	def update_parallelpcp(selected_point):
		text = selected_point["points"][0]["text"]
		text = text.split("Node: ")[1].split("<br>")[0]
		parallel_coordinate._prepare_plot_df(text)
		return parallel_coordinate.generate_figure()

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
			print(articles)
			return wordcloud.generate_wordcloud(articles, heatmap.company_name)

	@app.callback(
		Output("boxplot", "figure"),
		Input("heatmap", "clickData"),
		prevent_initial_call=True,
	)
	def display_articles(clickData):
		if clickData:
			point = clickData["points"][0]
			month = point["x"]
			source = point["y"]
			articles = heatmap.get_article(month, source)
			return sentiment_boxplot.get_boxplot_figure(articles, [source])
