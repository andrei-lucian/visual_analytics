from app.main import app
from app.load_df import *
from app.views.map import *
from app.views.dropdown import *
from app.views.barchart import *


from dash import html
from dash.dependencies import Input, Output
import json
import pandas as pd

if __name__ == '__main__':

	""" 
	This is the main layout of the webpage, its children are then sub divided
	into further html layouts 
	"""


	# Sample data: ISO country codes and values
	data = {
		"iso_alpha": ["USA", "CAN", "BRA", "FRA", "RUS", "CHN", "IND", "AUS", "ZAF"],
		"country": ["United States", "Canada", "Brazil", "France", "Russia", "China", "India", "Australia", "South Africa"],
		"value": [300, 150, 220, 180, 250, 500, 450, 170, 130]
	}

	data_df = pd.DataFrame(data)
	merged = full_df
	print(merged.columns)
	unique_genres_list = unique_genres

	choropleth_component = ChoroplethMap("World Map", data_df)

	genre_dropdown = Dropdown("Genre Dropdown", unique_genres_list)

	bar_chart = BarChartCard(
		name="Top Polarizing Movies (by Rating Std Dev)",
		df=merged,
		x_col="RatingStd",
		y_col="Title",
		top_n=10
	)

	# --- Styles ---
	sidebar_style = {
		"width": "15%",
		"backgroundColor": "#1e1e1e",
		"padding": "10px",
		"color": "white"
	}

	center_style = {
		"width": "85%",
		"display": "flex",
		"flexDirection": "column",
		"padding": "10px"
	}

	bottom_content_style = {
		"marginTop": "20px",
		"backgroundColor": "#26232C",
		"color": "white",
		"padding": "15px",
		"height": "200px"
	}

	main_content_style = {
		"display": "flex",
		"flexDirection": "row",
		"height": "100vh"
	}

	# --- App Layout ---
	app.layout = html.Div(id="app-container", children=[
		html.Div(id="top", className="top-bar", children=None),

		html.Div(id="main-content", style=main_content_style, children=[
			html.Div(id="left-column", style=sidebar_style, children=[genre_dropdown, bar_chart]),

			html.Div(id="center-column", style=center_style, children=[

				html.Div(id="bottom-content", style=bottom_content_style, children=[
					html.P("This area can be used for tables, insights, etc.")
				])
			])
		])
	])


	@app.callback(
		Output(bar_chart.html_id, 'figure'),
		Input(genre_dropdown.html_id, 'value'),
		)
	def update_barchart(dropdown_val):
		return bar_chart.update(dropdown_val)

	app.run_server(debug=True, dev_tools_ui=True)