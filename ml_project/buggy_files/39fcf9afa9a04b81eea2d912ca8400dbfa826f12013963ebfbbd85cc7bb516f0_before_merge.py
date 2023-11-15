    def __rmul__(self, X):
        """Y.__rmul__(X) <==> Y*X"""
        return mul(X, self)