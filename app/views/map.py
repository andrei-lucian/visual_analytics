from dash import dcc, html
import plotly.express as px

class ChoroplethMap(html.Div):
    def __init__(self, name, df, value_col="value", country_col="iso_alpha", hover_col="country"):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df
        self.value_col = value_col
        self.country_col = country_col
        self.hover_col = hover_col

        # Create the initial figure
        fig = self._create_figure()

        # Apply consistent styles
        super().__init__(
            className="graph_card",
            children=[
                dcc.Graph(
                    id=self.html_id,
                    figure=fig,
                    style={
                        'width': '100%',
                        'height': '450px',
                        'padding': 10,
                        'background-color': '#1e1e1e',  # Dark background for the graph container
                        'color': 'white',
                        'border': 'none'  # No border around the graph
                    }
                )
            ],
            style=dict(
                display='flex',
                backgroundColor='#1e1e1e',  # Dark background for the entire div
                color='white'
            )
        )

    def _create_figure(self):
        fig = px.choropleth(
            self.df,
            locations=self.country_col,
            color=self.value_col,
            hover_name=self.hover_col,
            color_continuous_scale=px.colors.sequential.Plasma
        )

        # Update layout to remove white background, borders, and title
        fig.update_layout(
            title=None,                     # Remove the title
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the figure
            plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot area (map area)
            geo=dict(
                bgcolor='rgba(0,0,0,0)'     # Transparent map background
            ),
            font=dict(color='white'),        # Set text color to white
            margin=dict(l=0, r=0, t=0, b=0), # Remove margin around the map to eliminate any borders
            coloraxis_showscale=False       # Remove color scale (optional)
        )

        return fig