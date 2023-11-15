    def __init__(self, linter=None):
        BaseChecker.__init__(self, linter)
        self._accessed = ScopeAccessMap()
        self._first_attrs = []
        self._meth_could_be_func = None