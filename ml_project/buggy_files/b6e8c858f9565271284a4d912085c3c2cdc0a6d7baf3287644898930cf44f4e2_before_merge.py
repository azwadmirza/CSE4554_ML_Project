    def __init__(self, max_line_length=80, tab_space_size=4, indent_unit='space', **kwargs):
        """Initialise, getting the max line length."""
        self.max_line_length = max_line_length
        # Call out tab_space_size and indent_unit to make it clear they're still options.
        super(Rule_L016, self).__init__(
            tab_space_size=tab_space_size, indent_unit=indent_unit,
            **kwargs)