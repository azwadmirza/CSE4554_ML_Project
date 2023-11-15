        def __init__(self, *args, **kwargs):
            first, args = args[0], args[1:]
            super(self, _BoundedDist).__init__(first, distribution, lower, upper, *args, **kwargs)