    def __init__(self):
        """For the indent we override the init method.

        For something without content, neither makes sense.
        """
        self._raw = ''
        self.pos_marker = None