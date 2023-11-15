    def __init__(self, signal1D, auto_background=True,
                 auto_add_edges=True, ll=None,
                 GOS=None, dictionary=None):
        Model1D.__init__(self, signal1D)
        self._suspend_auto_fine_structure_width = False
        self.convolved = False
        self.low_loss = ll
        self.GOS = GOS
        self.edges = []
        self._background_components = []
        if dictionary is not None:
            auto_background = False
            auto_add_edges = False
            self._load_dictionary(dictionary)

        if auto_background is True:
            background = PowerLaw()
            self.append(background)

        if self.signal.subshells and auto_add_edges is True:
            self._add_edges_from_subshells_names()