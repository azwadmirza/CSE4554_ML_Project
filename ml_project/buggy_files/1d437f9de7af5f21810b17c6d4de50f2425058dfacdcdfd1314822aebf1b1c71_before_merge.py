    def __init__(self, func, identity=None, cache=False, targetoptions={}):
        if cache:
            raise TypeError("caching is not supported")
        assert not targetoptions
        self.py_func = func
        self.identity = parse_identity(identity)
        # { arg_dtype: (return_dtype), cudakernel }
        self.kernelmap = OrderedDict()