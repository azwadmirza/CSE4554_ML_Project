    def __init__(self, axis=0, matrix=False, ndmin=1, trans1d=-1):
        self._axis = axis
        self._matrix = matrix
        self.axis = axis
        self.matrix = matrix
        self.col = 0
        self.trans1d = trans1d
        self.ndmin = ndmin