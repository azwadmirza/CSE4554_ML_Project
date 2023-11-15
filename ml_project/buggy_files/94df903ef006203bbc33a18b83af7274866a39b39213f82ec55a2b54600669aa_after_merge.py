    def array_angle_impl(arr, deg):
        out = numpy.zeros_like(arr, dtype=ret_dtype)
        for index, val in numpy.ndenumerate(arr):
            out[index] = numpy.angle(val, deg)
        return out