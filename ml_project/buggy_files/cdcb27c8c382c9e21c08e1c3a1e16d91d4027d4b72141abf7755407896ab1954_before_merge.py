    def _get_colors():
        #  num_colors=3 is required as method maybe_color_bp takes the colors
        #  in positions 0 and 2.
        return _get_standard_colors(color=kwds.get("color"), num_colors=3)