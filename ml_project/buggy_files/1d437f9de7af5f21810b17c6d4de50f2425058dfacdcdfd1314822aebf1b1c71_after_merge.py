    def __init__(self, func, identity=None, cache=False, targetoptions={}):
        if cache:
            raise TypeError("caching is not supported")
        for opt in targetoptions:
            if opt == 'nopython':
                warnings.warn("nopython kwarg for cuda target is redundant",
                              RuntimeWarning)
            else:
                fmt = "cuda vectorize target does not support option: '%s'"
                raise KeyError(fmt % opt)
        self.py_func = func
        self.identity = parse_identity(identity)
        # { arg_dtype: (return_dtype), cudakernel }
        self.kernelmap = OrderedDict()