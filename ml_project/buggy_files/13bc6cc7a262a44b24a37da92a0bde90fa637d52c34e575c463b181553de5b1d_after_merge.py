        def array_argmin_impl(arry):
            if arry.size == 0:
                raise ValueError("attempt to get argmin of an empty sequence")
            for v in arry.flat:
                min_value = v
                min_idx = 0
                break

            idx = 0
            for v in arry.flat:
                if v < min_value:
                    min_value = v
                    min_idx = idx
                idx += 1
            return min_idx