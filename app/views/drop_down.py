from dash import html, dcc

class CountryDropdown(html.Div):
    def __init__(self, name, df, value_col="country"):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df
        self.value_col = value_col

        options = [{"label": country, "value": country} for country in df[value_col]]

        super().__init__(
            className="graph_card",
            style={
                "padding": "10px",
                "backgroundColor": "#26232C",
                "color": "white",
                "marginBottom": "15px"
            },
            children=[
                html.Label(f"Select {name}", style={
                    "color": "white",
                    "marginBottom": "5px",
                    "display": "block"
                }),
                dcc.Dropdown(
                    id=self.html_id,
                    options=options,
                    value=options[0]["value"],
                    clearable=False,
                    style={
                        "backgroundColor": "#1e1e1e",
                        "color": "black",
                        "border": "1px solid #555",
                        "borderRadius": "5px"
                    }
                )
            ]
        )