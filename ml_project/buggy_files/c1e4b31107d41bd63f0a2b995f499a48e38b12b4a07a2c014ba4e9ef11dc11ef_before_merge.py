def _pat_wrapper(f, flags=False):
    def wrapper1(self, pat):
        result = f(self.series, pat)
        return self._wrap_result(result)

    def wrapper2(self, pat, flags=0):
        result = f(self.series, pat, flags=flags)
        return self._wrap_result(result)

    wrapper = wrapper2 if flags else wrapper1

    wrapper.__name__ = f.__name__
    if f.__doc__:
        wrapper.__doc__ = f.__doc__

    return wrapper