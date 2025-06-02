from dash import dcc, html


class YearRangeSlider(html.Div):
    def __init__(self, df, year_col="Year", name="Year Range"):
        self.df = df
        self.year_col = year_col
        self.html_id = name.lower().replace(" ", "-") + "-range-slider"

        min_year = int(df[year_col].min())
        max_year = int(df[year_col].max())

        super().__init__(
            className="graph_card",
            style={"padding": "10px", "backgroundColor": "#26232C", "color": "white", "marginBottom": "15px"},
            children=[
                html.Label(f"{name}", style={"color": "white", "marginBottom": "5px", "display": "block"}),
                dcc.RangeSlider(
                    id=self.html_id,
                    min=min_year,
                    max=max_year,
                    step=1,
                    value=[2010, 2025],
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True},
                    allowCross=False,
                ),
            ],
        )
