    def impl(a, b):
        a_ = np.asarray(a)
        b_ = np.asarray(b)
        if a_.shape[-1] not in (2, 3) or b_.shape[-1] not in (2, 3):
            raise ValueError((
                "Incompatible dimensions for cross product\n"
                "(dimension must be 2 or 3)"
            ))

        if a_.shape[-1] == 3 or b_.shape[-1] == 3:
            return _cross_impl(a_, b_)
        else:
            raise ValueError((
                "Dimensions for both inputs is 2.\n"
                "Please replace your numpy.cross(a, b) call with "
                "a call to `cross2d(a, b)` from `numba.np.extensions`."
            ))