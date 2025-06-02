from dash import html, dcc


class Dropdown(html.Div):
    def __init__(self, name, df, value_col="country"):
        self.html_id = name.lower().replace(" ", "-") + "-dropdown"
        self.df = df
        self.value_col = value_col

        options = df

        super().__init__(
            className="graph_card",
            style={"padding": "10px", "backgroundColor": "#26232C", "color": "white", "marginBottom": "15px"},
            children=[
                html.Label(f"{name}", style={"color": "white", "marginBottom": "5px", "display": "block"}),
                dcc.Dropdown(
                    id=self.html_id,
                    options=options,
                    multi=True,
                    value=[options[0], options[3]],
                    clearable=False,
                    style={
                        "backgroundColor": "#1e1e1e",
                        "color": "black",
                        "border": "1px solid #555",
                        "borderRadius": "5px",
                    },
                ),
            ],
        )
