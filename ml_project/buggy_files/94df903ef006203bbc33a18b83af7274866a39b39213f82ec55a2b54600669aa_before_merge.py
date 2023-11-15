    def array_angle_impl(arr, deg=False):
        out = numpy.zeros_like(arr, dtype=retty)
        for index, val in numpy.ndenumerate(arr):
            out[index] = numpy.angle(val, deg)
        return out