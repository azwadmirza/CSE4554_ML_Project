    def _is_valid_index(x):
        return (com.is_integer(x) or com.is_float(x)
                and np.allclose(x, int(x), rtol=_eps, atol=0))