from dash import html, dcc
import plotly.express as px

class BarChartCard(html.Div):
	def __init__(self, name, df, x_col, y_col, hover_cols=None, top_n=10):
		self.html_id = name.lower().replace(" ", "-") + "-bar-chart"
		self.df = df
		self.x_col = x_col
		self.y_col = y_col
		self.hover_cols = hover_cols if hover_cols else []
		self.top_n = top_n
		self.exploded_df = None

		# calculate std deviation
		stats = self.df.groupby('MovieID').agg(
			Title=('Title', 'first'),
			RatingCount=('Rating', 'count'),
			RatingStd=('Rating', 'std'),
			Year=('Year', 'first'),
			Genres=('Genres', 'first')
		).reset_index()

		# Sort by standard deviation 
		stats = stats.sort_values(by='RatingStd', ascending=False)
		stats['GenreList'] = stats['Genres'].str.split('|')
		self.exploded_df = stats.explode('GenreList')
		

		fig = px.bar(
			stats.head(self.top_n),
			x=self.x_col,
			y=self.y_col,
			orientation='h',
			hover_data=self.hover_cols,
			title=name
		)

		fig.update_layout(yaxis={'categoryorder': 'total ascending'},
						  plot_bgcolor='#26232C',
						  paper_bgcolor='#26232C',
						  font_color='white')

		super().__init__(
			className="graph_card",
			style={
				"padding": "10px",
				"backgroundColor": "#26232C",
				"color": "white",
				"marginBottom": "15px"
			},
			children=[
				html.Label(name, style={
					"color": "white",
					"marginBottom": "5px",
					"display": "block"
				}),
				dcc.Graph(
					id=self.html_id,
					figure=fig,
					config={'displayModeBar': False}
				)
			]
		)
		
	def update(self, genre_filter):
		# Filter your DataFrame by the selected genre
		filtered_df = self.exploded_df[self.exploded_df['GenreList'] == genre_filter]
		
		# Sort and pick top N if needed
		top_n = 10
		filtered_top = filtered_df.sort_values('RatingStd', ascending=False).head(top_n)
		

		# Create the updated figure
		fig = px.bar(
			filtered_top,
			x='RatingStd',
			y='Title',
			orientation='h',
			hover_data=['Year', 'RatingCount'],
			title=f"Top Polarizing {genre_filter} Movies"
		)
		fig.update_layout(yaxis={'categoryorder': 'total ascending'},
						plot_bgcolor='#26232C',
						paper_bgcolor='#26232C',
						font_color='white')

		return fig