from dash import html, dcc


class Checklist(html.Div):
    def __init__(self, name, options, value=None):
        """
        options: list of dicts with keys 'label' and 'value', e.g.
            [{'label': 'Action', 'value': 'Action'}, ...]
        value: list of selected values (default all selected)
        """
        self.html_id = name.lower().replace(" ", "-") + "-checkbox"
        if value is None:
            value = [opt["value"] for opt in options]  # default select all

        super().__init__(
            className="graph_card",
            style={"padding": "10px", "backgroundColor": "#26232C", "color": "white", "marginBottom": "15px"},
            children=[
                html.Label(name, style={"color": "white", "marginBottom": "5px", "display": "block"}),
                dcc.Checklist(
                    id=self.html_id,
                    options=options,
                    value=value,
                    inputStyle={"margin-right": "5px", "margin-left": "10px"},
                    labelStyle={"display": "block", "color": "white", "cursor": "pointer"},
                ),
            ],
        )
