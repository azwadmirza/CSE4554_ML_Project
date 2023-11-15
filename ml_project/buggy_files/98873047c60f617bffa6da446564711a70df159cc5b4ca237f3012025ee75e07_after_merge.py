    def _is_sparse(cls, x1, x2):
        if hasattr(x1, 'issparse') and x1.issparse():
            # if x1 is sparse, will be sparse always
            return True
        elif np.isscalar(x1) and x1 == 0:
            # x1 == 0, return sparse if x2 is
            return x2.issparse() if hasattr(x2, 'issparse') else False
        return False