    def __call__(self, projectables, **info):

        c01, c02, c03 = projectables

        r = c02
        b = c01
        g = simulated_green(c01, c02, c03)

        return super(TrueColor2km, self).__call__((r, g, b), **info)