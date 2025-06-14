from dash import dcc, html


class EdgeTypeDropdown:
    def __init__(self, options, html_id):
        self.options = options
        self.html_id = html_id

    def render(self):
        return dcc.Dropdown(
            id=self.html_id,
            options=self.options,
            value=[self.options[0], self.options[1]],  # default select all
            multi=True,
            placeholder="Select edge types",
            clearable=False,
        )
