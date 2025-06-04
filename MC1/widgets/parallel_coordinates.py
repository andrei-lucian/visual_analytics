import json
import pandas as pd
import plotly.graph_objects as go
from dash import dcc

class ParallelCoordinatesPlot:
	def __init__(self, json_path, html_id):
		self.json_path = json_path
		self.html_id = html_id

		self.data = self._load_data()
		self.df_nodes, self.df_links = self._create_dfs()
		self.edge_types_available = self._get_edge_types()
		self.color_map = self._generate_color_map()
		self._prepare_plot_df(None)
		self.fig = self._create_figure()


	def _load_data(self):
		with open(self.json_path, 'r') as f:
			return json.load(f)

	def _create_dfs(self):
		nodes = self.data["nodes"]
		links = self.data["links"]
		return pd.DataFrame(nodes), pd.DataFrame(links)

	def _get_edge_types(self):
		return self.df_links['type'].unique()

	def _generate_color_map(self):
		# Map _algorithm strings to numbers for coloring
		return {'BassLine': 0, 'ShadGPT': 1}

	def _counts_to_full_dict(self, counts, all_types):
		return {t: counts.get(t, 0) for t in all_types}

	def _prepare_plot_df(self, selected_point = None):
		if selected_point == None:
			filtered_df = self.df_links[self.df_links['target'] == 'Namorna Transit Ltd']
		else:
			filtered_df = self.df_links[self.df_links['target'] == selected_point]

		df_baseline = filtered_df[filtered_df['_algorithm'] == 'BassLine']
		df_shadgpt = filtered_df[filtered_df['_algorithm'] == 'ShadGPT']

		all_types = self.edge_types_available

		counts_baseline = df_baseline['type'].value_counts()
		counts_shadgpt = df_shadgpt['type'].value_counts()

		counts_baseline_full = self._counts_to_full_dict(counts_baseline, all_types)
		counts_shadgpt_full = self._counts_to_full_dict(counts_shadgpt, all_types)

		df_plot = pd.DataFrame([counts_baseline_full, counts_shadgpt_full])
		df_plot['_algorithm'] = ['BassLine', 'ShadGPT']
		df_plot['_algorithm_code'] = df_plot['_algorithm'].map(self.color_map)

		self.df_plot = df_plot

	def _create_figure(self):
		dimensions = []
		for col in self.edge_types_available:
			max_val = self.df_plot[col].max()
			if max_val == 0:
				max_val = 1  # avoid zero range error
			dimensions.append(dict(
				range=[0, max_val],
				label=col,
				values=self.df_plot[col]
			))

		fig = go.Figure(data=go.Parcoords(
			line=dict(color=self.df_plot['_algorithm_code'], colorscale='Portland', showscale=True),
			dimensions=dimensions
		))
		return fig

	def render(self):
		"""Return the Dash dcc.Graph component to embed in a layout."""
		return dcc.Graph(id=self.html_id, figure=self.fig)
	