from dash.dependencies import Input, Output
from app.views.layout import *


def register_callbacks(app):
    # @app.callback(
    #     Output(bar_chart.html_id, "figure"),
    #     Input(genre_dropdown.html_id, "value"),
    # )
    # def update_barchart(dropdown_val):
    #     return bar_chart.update(dropdown_val)

    # Scatter plot
    @app.callback(
        Output(scatter_plot.html_id, "figure"),
        [
            Input(genre_dropdown.html_id, "value"),  # now a list
            Input(year_slider.html_id, "value"),
        ],
    )
    def update_scatter(selected_genres, year_range):
        min_year, max_year = year_range

        # Handle no genre selected
        if not selected_genres:
            genre_filtered_df = merged_df.copy()
        else:
            # Build regex pattern to match any selected genre
            pattern = "|".join([rf"\b{genre}\b" for genre in selected_genres])
            genre_filtered_df = merged_df[merged_df["Genre"].str.contains(pattern, case=False, na=False)]

        # Filter by year
        filtered_df = genre_filtered_df[
            (genre_filtered_df["Year"] >= min_year) & (genre_filtered_df["Year"] <= max_year)
        ]

        # Build color mapping
        color_map = px.colors.qualitative.Plotly
        all_genres = sorted(set(g.strip() for sublist in merged_df["Genre"].dropna().str.split(",") for g in sublist))
        genre_color_dict = {genre: color_map[i % len(color_map)] for i, genre in enumerate(all_genres)}

        # Choose first matched genre for coloring
        def pick_primary_genre(genre_string):
            genres = [g.strip() for g in genre_string.split(",")] if pd.notnull(genre_string) else []
            for g in genres:
                if g in selected_genres:
                    return g
            return genres[0] if genres else None

        primary_genres = filtered_df["Genre"].apply(pick_primary_genre)
        point_colors = primary_genres.map(genre_color_dict)

        fig = {
            "data": [
                {
                    "x": filtered_df["pca_x"],
                    "y": filtered_df["pca_y"],
                    "mode": "markers",
                    "marker": {"size": 12, "color": point_colors},
                    "type": "scatter",
                    "text": filtered_df["Title_x"],
                    "hoverinfo": "text",
                }
            ],
            "layout": {
                "title": f"Movies ({min_year} - {max_year})",
                "xaxis": {"title": "pca_x"},
                "yaxis": {"title": "pca_y"},
                "height": 400,
                "plot_bgcolor": "#26232C",
                "paper_bgcolor": "#26232C",
                "font": {"color": "white"},
            },
        }
        return fig

    # Stream graph
    @app.callback(
        Output(stream_graph.html_id, "figure"),
        Input(genre_dropdown.html_id, "value"),  # value might be str or list
    )
    def update_streamgraph(selected_genres):
        # If nothing selected, show all genres
        if not selected_genres:
            filtered_pivot = genre_pivot
        else:
            # Ensure selected_genres is a list
            if isinstance(selected_genres, str):
                selected_genres = [selected_genres]

            filtered_pivot = genre_pivot.reindex(columns=selected_genres, fill_value=0)

        return stream_graph.create_streamgraph(filtered_pivot)

    # Line plot
    @app.callback(
        Output(line_plot.html_id, "figure"),
        Input(genre_dropdown.html_id, "value"),
    )
    def update_lineplot(selected_genres):
        return line_plot.create_figure(genre_year_avg_rating, selected_genres)
