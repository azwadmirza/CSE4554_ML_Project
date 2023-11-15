    def scalar_angle_impl(val, deg):
        if deg:
            return numpy.arctan2(val.imag, val.real) * deg_mult
        else:
            return numpy.arctan2(val.imag, val.real)