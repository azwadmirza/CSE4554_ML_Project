    def __radd__(self, X):
        """Y.__radd__(X) <==> Y+X"""
        return add(self, X)