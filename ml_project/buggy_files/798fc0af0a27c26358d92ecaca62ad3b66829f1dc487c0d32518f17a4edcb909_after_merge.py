        def nanmedian_impl(arry):
            # Create a temporary workspace with only non-NaN values
            temp_arry = np.empty(arry.size, arry.dtype)
            n = 0
            for view in np.nditer(arry):
                v = view.item()
                if not isnan(v):
                    temp_arry[n] = v
                    n += 1

            # all NaNs
            if n == 0:
                return np.nan

            return _median_inner(temp_arry, n)