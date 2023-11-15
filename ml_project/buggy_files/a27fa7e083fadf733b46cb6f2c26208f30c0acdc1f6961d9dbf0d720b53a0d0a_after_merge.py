    def __init__(self, pos_marker):
        """For the indent we override the init method.

        For something without content, the content doesn't make
        sense. The pos_marker, will be matched with the following
        segment, but meta segments are ignored during fixes so it's
        ok in this sense. We need the pos marker later for dealing
        with repairs.
        """
        self._raw = ''
        # TODO: Make sure that we DO actually skip meta segments
        # during fixes.
        self.pos_marker = pos_marker