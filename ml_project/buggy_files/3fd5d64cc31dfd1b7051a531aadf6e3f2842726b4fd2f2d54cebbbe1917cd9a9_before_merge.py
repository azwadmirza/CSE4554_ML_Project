        def split_impl(a, sep, maxsplit=-1):
            a_len = len(a)
            sep_len = len(sep)

            if sep_len == 0:
                raise ValueError('empty separator')

            parts = []
            last = 0
            idx = 0

            if sep_len == 1 and maxsplit == -1:
                sep_code_point = _get_code_point(sep, 0)
                for idx in range(a_len):
                    if _get_code_point(a, idx) == sep_code_point:
                        parts.append(a[last:idx])
                        last = idx + 1
            else:
                split_count = 0

                while idx < a_len and (maxsplit == -1 or
                                       split_count < maxsplit):
                    if _cmp_region(a, idx, sep, 0, sep_len) == 0:
                        parts.append(a[last:idx])
                        idx += sep_len
                        last = idx
                        split_count += 1
                    else:
                        idx += 1

            if last <= a_len:
                parts.append(a[last:])

            return parts