from dash import html, dcc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


class StreamGraph(html.Div):
    def __init__(self, df, year_col="Year", genre_col="Genre", height=300):
        self.df = df
        self.year_col = year_col
        self.genre_col = genre_col
        self.html_id = "stream-graph"
        super().__init__(
            className="graph_card",
            style={
                "padding": "10px",
                "backgroundColor": "#26232C",
                "color": "white",
                "marginBottom": "15px",
            },
            children=[dcc.Graph(id=self.html_id, figure=self.create_streamgraph(df))],  # initial full data figure
        )

    def create_streamgraph(self, df):
        fig = go.Figure()

        genres = df.columns
        x = df.index

        # Initialize base for stream layers (for stacking)
        base = [0] * len(x)

        color_map = px.colors.qualitative.Plotly

        for i, genre in enumerate(genres):
            y = df[genre].values
            y0 = base
            y1 = base = [y0[j] + y[j] for j in range(len(y))]

            fig.add_trace(
                go.Scatter(
                    x=list(x) + list(x[::-1]),
                    y=list(y0) + list(y1[::-1]),
                    fill="toself",
                    mode="none",
                    name=genre,
                    fillcolor=color_map[i % len(color_map)],
                    hoverinfo="x+name+y",
                )
            )

        fig.update_layout(
            title="Genre Popularity Over Time (Streamgraph)",
            xaxis_title="Year",
            yaxis_title="Number of Movies",
            showlegend=True,
            plot_bgcolor="#26232C",
            paper_bgcolor="#26232C",
            font={"color": "white"},
            margin=dict(l=20, r=20, t=40, b=20),
        )

        return fig
