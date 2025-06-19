from dash import dcc


class EdgeTypeDropdown:
    def __init__(self, options, html_id):
        """
        Initialize the dropdown component.

        Parameters:
        - options (list): A list of options to display in the dropdown.
        - html_id (str): The HTML ID to associate with the Dash component.
        """
        self.options = options
        self.html_id = html_id

    def render(self):
        """
        Render the Dash Dropdown component.

        Returns:
        - dcc.Dropdown: A Dash dropdown component with the specified options and settings.
        """
        return dcc.Dropdown(
            id=self.html_id,
            options=self.options,
            value=[self.options[0], self.options[1]],
            multi=True,
            placeholder="Select edge types",
            clearable=False,
        )
