    def f(x):
        if isinstance(x, dict):
            return x.get(i)
        elif len(x) > i >= -len(x):
            return x[i]
        return np.nan