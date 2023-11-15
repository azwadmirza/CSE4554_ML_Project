    def __init__(self, dist, *args, **kwds):
        self.args = args
        self.kwds = kwds

        # create a new instance
        self.dist = dist.__class__(**dist._updated_ctor_param())

        shapes, _, _ = self.dist._parse_args(*args, **kwds)
        self.dist._argcheck(*shapes)
        self.a, self.b = self.dist._get_support(*args, **kwds)