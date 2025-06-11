import json
import pandas as pd
import plotly.graph_objects as go
from dash import dcc


class HorizontalBarPlot:
	def __init__(self, data, html_id):
		self.html_id = html_id
		self.data = data
		self.edge_type_sentiment = {
			"Event.Applaud": "positive",
			"Event.Aid": "positive",
			"Event.Invest": "positive",
			"Event.Fishing.SustainableFishing": "positive",
			"Event.Criticize": "negative",
			"Event.Convicted": "negative",
			"Event.CertificateIssued.Summons": "negative",
			"Event.Fishing.OverFishing": "negative",
			"Event.CertificateIssued": "neutral",
			"Event.Transaction": "neutral",
			"Event.Fishing": "neutral",
			"Event.Owns.PartiallyOwns": "neutral",
			"Event.Communication.Conference": "neutral",
		}
		self.df_nodes, self.df_links = self._create_dfs()
		self.edge_types_available = self._get_edge_types()
		self.color_map = self._generate_color_map()
		self._prepare_plot_df(None)
		self.fig = self.generate_figure()

	def _create_dfs(self):
		nodes = self.data["nodes"]
		links = self.data["links"]
		return pd.DataFrame(nodes), pd.DataFrame(links)

	def _get_edge_types(self):
		types = self.df_links["type"].unique()
		sentiment_order = {"negative": 0, "neutral": 1, "positive": 2}
		return sorted(types, key=lambda x: sentiment_order.get(self.edge_type_sentiment.get(x, "neutral"), 1))

	def _generate_color_map(self):
		# Map _algorithm strings to numbers for coloring
		return {"BassLine": 0, "ShadGPT": 1}

	def _counts_to_full_dict(self, counts, all_types):
		return {t: counts.get(t, 0) for t in all_types}

	def _prepare_plot_df(self, selected_point=None):
		if selected_point == None:
			filtered_df = self.df_links[
				(self.df_links["source"] == "Namorna Transit Ltd") | (self.df_links["target"] == "Namorna Transit Ltd")
			]
		else:
			filtered_df = self.df_links[
				(self.df_links["source"] == selected_point) | (self.df_links["target"] == selected_point)
			]

		df_baseline = filtered_df[filtered_df["_algorithm"] == "BassLine"]
		df_shadgpt = filtered_df[filtered_df["_algorithm"] == "ShadGPT"]

		all_types = self.edge_types_available

		counts_baseline = df_baseline["type"].value_counts()
		counts_shadgpt = df_shadgpt["type"].value_counts()

		counts_baseline_full = self._counts_to_full_dict(counts_baseline, all_types)
		counts_shadgpt_full = self._counts_to_full_dict(counts_shadgpt, all_types)

		df_plot = pd.DataFrame([counts_baseline_full, counts_shadgpt_full])
		df_plot["_algorithm"] = ["BassLine", "ShadGPT"]
		df_plot["_algorithm_code"] = df_plot["_algorithm"].map(self.color_map)

		self.df_plot = df_plot
		
	def generate_figure(self):
		fig = go.Figure()

		colors = {
			"BassLine": "blue",
			"ShadGPT": "orange",
		}

		for alg in ["BassLine", "ShadGPT"]:
			df_alg = self.df_plot[self.df_plot["_algorithm"] == alg]
			fig.add_trace(
				go.Bar(
					y=self.edge_types_available,
					x=df_alg[self.edge_types_available].values.flatten(),
					name=alg,
					orientation="h",
					marker_color=colors.get(alg, "gray"),
				)
			)

		# Add background color blocks for sentiment groups
		shapes = []
		y_labels = list(self.edge_types_available)
		sentiment_groups = {"negative": "red", "neutral": "white", "positive": "green"}

		y_index = {label: i for i, label in enumerate(y_labels)}
		current_group = None
		start = None

		for i, label in enumerate(y_labels + [None]):  # add sentinel
			sentiment = self.edge_type_sentiment.get(label, "neutral") if label else None

			if sentiment != current_group:
				if current_group is not None:
					# Use numerical y-index for precise alignment
					y0 = y_index[y_labels[start]] - 0.5
					y1 = y_index[y_labels[i - 1]] + 0.5
					shapes.append(
						dict(
							type="rect",
							xref="paper",
							yref="y",
							x0=0,
							x1=1,
							y0=y0,
							y1=y1,
							fillcolor=sentiment_groups[current_group],
							opacity=0.2,
							layer="below",
							line_width=0,
						)
					)
				current_group = sentiment
				start = i

		fig.update_layout(
			barmode="stack",
			title="Edge Type Counts by Algorithm",
			xaxis_title="Count",
			yaxis_title="Edge Type",
			legend_title="Algorithm",
			shapes=shapes,
		)
		return fig

	def render(self):
		"""Return the Dash dcc.Graph component to embed in a layout."""
		return dcc.Graph(id=self.html_id, figure=self.fig)
