    def array_argmax_impl(arry):
        if arry.size == 0:
            raise ValueError("attempt to get argmax of an empty sequence")
        for v in arry.flat:
            max_value = v
            max_idx = 0
            break

        idx = 0
        for v in arry.flat:
            if v > max_value:
                max_value = v
                max_idx = idx
            idx += 1
        return max_idx