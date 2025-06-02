from dash import dcc, html

pcp_plot_component = html.Div([html.H3("Parallel Coordinates Plot"), dcc.Graph(id="pcp-graph")])
