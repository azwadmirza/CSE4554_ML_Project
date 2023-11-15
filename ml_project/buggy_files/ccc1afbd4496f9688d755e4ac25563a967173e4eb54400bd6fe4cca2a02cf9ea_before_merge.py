    def scalar_angle_impl(val, deg=False):
        if deg:
            scal = 180/numpy.pi
            return numpy.arctan2(val.imag, val.real) * scal
        else:
            return numpy.arctan2(val.imag, val.real)