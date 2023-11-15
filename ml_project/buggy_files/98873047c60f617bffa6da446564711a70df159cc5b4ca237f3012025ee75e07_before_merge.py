    def _is_sparse(cls, x1, x2):
        # x2 is sparse or not does not matter
        if hasattr(x1, 'issparse') and x1.issparse() and np.isscalar(x2):
            return True
        elif x1 == 0:
            return True
        return False