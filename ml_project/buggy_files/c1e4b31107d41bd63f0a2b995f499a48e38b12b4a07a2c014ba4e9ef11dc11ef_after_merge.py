def _pat_wrapper(f, flags=False, na=False):
    def wrapper1(self, pat):
        result = f(self.series, pat)
        return self._wrap_result(result)

    def wrapper2(self, pat, flags=0):
        result = f(self.series, pat, flags=flags)
        return self._wrap_result(result)

    def wrapper3(self, pat, na=np.nan):
        result = f(self.series, pat, na=na)
        return self._wrap_result(result)

    wrapper = wrapper3 if na else wrapper2 if flags else wrapper1

    wrapper.__name__ = f.__name__
    if f.__doc__:
        wrapper.__doc__ = f.__doc__

    return wrapper