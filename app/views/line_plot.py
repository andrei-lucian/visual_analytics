from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px


class LinePlot(html.Div):
    def __init__(self, df, year_col="Year", genre_col="GenreList", rating_col="imdbRating", height=300):
        self.df = df
        self.year_col = year_col
        self.genre_col = genre_col
        self.rating_col = rating_col
        self.html_id = "line-plot"
        super().__init__(
            className="graph_card",
            style={
                "padding": "10px",
                "backgroundColor": "#26232C",
                "color": "white",
                "marginBottom": "15px",
            },
            children=[dcc.Graph(id=self.html_id, figure=self.create_figure(df))],
        )

    def create_figure(self, df, selected_genres=None):
        fig = go.Figure()
        color_map = px.colors.qualitative.Plotly

        # Filter genres if provided
        if selected_genres:
            if isinstance(selected_genres, str):
                selected_genres = [selected_genres]
            df = df[df[self.genre_col].isin(selected_genres)]
        else:
            selected_genres = df[self.genre_col].unique()

        for i, genre in enumerate(selected_genres):
            genre_df = df[df[self.genre_col] == genre]
            genre_df = genre_df.sort_values(self.year_col)

            fig.add_trace(
                go.Scatter(
                    x=genre_df[self.year_col],
                    y=genre_df[self.rating_col],
                    mode="lines+markers",
                    name=genre,
                    line=dict(color=color_map[i % len(color_map)]),
                )
            )

        fig.update_layout(
            title="Average Rating Over Time by Genre",
            xaxis_title="Year",
            yaxis_title="Average Rating",
            plot_bgcolor="#26232C",
            paper_bgcolor="#26232C",
            font={"color": "white"},
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(range=[0, 10]),  # Assuming ratings 0-5 scale
        )

        return fig
