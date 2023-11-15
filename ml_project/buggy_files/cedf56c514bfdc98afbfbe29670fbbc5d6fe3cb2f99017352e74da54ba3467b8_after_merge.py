    def impl(x, xp, fp, dtype):
        # NOTE: Do not refactor... see note in np_interp function impl below
        # this is a facsimile of arr_interp post 1.16:
        # https://github.com/numpy/numpy/blob/maintenance/1.16.x/numpy/core/src/multiarray/compiled_base.c    # noqa: E501
        # Permanent reference:
        # https://github.com/numpy/numpy/blob/971e2e89d08deeae0139d3011d15646fdac13c92/numpy/core/src/multiarray/compiled_base.c#L473     # noqa: E501
        dz = np.asarray(x, dtype=np.float64)
        dx = np.asarray(xp, dtype=np.float64)
        dy = np.asarray(fp, dtype=np.float64)

        if len(dx) == 0:
            raise ValueError('array of sample points is empty')

        if len(dx) != len(dy):
            raise ValueError('fp and xp are not of the same size.')

        if dx.size == 1:
            return np.full(dz.shape, fill_value=dy[0], dtype=dtype)

        dres = np.empty(dz.shape, dtype=dtype)

        lenx = dz.size
        lenxp = len(dx)
        lval = dy[0]
        rval = dy[lenxp - 1]

        if lenxp == 1:
            xp_val = dx[0]
            fp_val = dy[0]

            for i in range(lenx):
                x_val = dz.flat[i]
                if x_val < xp_val:
                    dres.flat[i] = lval
                elif x_val > xp_val:
                    dres.flat[i] = rval
                else:
                    dres.flat[i] = fp_val

        else:
            j = 0

            # only pre-calculate slopes if there are relatively few of them.
            if lenxp <= lenx:
                slopes = (dy[1:] - dy[:-1]) / (dx[1:] - dx[:-1])
            else:
                slopes = np.empty(0, dtype=dtype)

            for i in range(lenx):
                x_val = dz.flat[i]

                if np.isnan(x_val):
                    dres.flat[i] = x_val
                    continue

                j = binary_search_with_guess(x_val, dx, lenxp, j)

                if j == -1:
                    dres.flat[i] = lval
                elif j == lenxp:
                    dres.flat[i] = rval
                elif j == lenxp - 1:
                    dres.flat[i] = dy[j]
                elif dx[j] == x_val:
                    # Avoid potential non-finite interpolation
                    dres.flat[i] = dy[j]
                else:
                    if slopes.size:
                        slope = slopes[j]
                    else:
                        slope = (dy[j + 1] - dy[j]) / (dx[j + 1] - dx[j])

                    dres.flat[i] = slope * (x_val - dx[j]) + dy[j]

                    # NOTE: this is in np1.17
                    # https://github.com/numpy/numpy/blob/maintenance/1.17.x/numpy/core/src/multiarray/compiled_base.c    # noqa: E501
                    # Permanent reference:
                    # https://github.com/numpy/numpy/blob/91fbe4dde246559fa5b085ebf4bc268e2b89eea8/numpy/core/src/multiarray/compiled_base.c#L610-L616    # noqa: E501
                    #
                    # If we get nan in one direction, try the other
                    if np117_nan_handling:
                        if np.isnan(dres.flat[i]):
                            dres.flat[i] = slope * (x_val - dx[j + 1]) + dy[j + 1]    # noqa: E501
                            if np.isnan(dres.flat[i]) and dy[j] == dy[j + 1]:
                                dres.flat[i] = dy[j]

        return dres