        def array_min_impl(arry):
            if arry.size == 0:
                raise ValueError(("zero-size array to reduction operation "
                                  "minimum which has no identity"))
            it = np.nditer(arry)
            for view in it:
                min_value = view.item()
                break

            for view in it:
                v = view.item()
                if v < min_value:
                    min_value = v
            return min_value