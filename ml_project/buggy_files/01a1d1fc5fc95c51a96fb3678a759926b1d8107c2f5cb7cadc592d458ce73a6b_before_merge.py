def unicode_split(a, sep=None, maxsplit=-1):
    if not (maxsplit == -1 or
            isinstance(maxsplit, (types.Omitted, types.Integer,
                                  types.IntegerLiteral))):
        return None  # fail typing if maxsplit is not an integer

    if isinstance(sep, types.UnicodeType):
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
        return split_impl
    elif sep is None or isinstance(sep, types.NoneType) or \
            getattr(sep, 'value', False) is None:
        def split_whitespace_impl(a, sep=None, maxsplit=-1):
            a_len = len(a)

            parts = []
            last = 0
            idx = 0
            split_count = 0
            in_whitespace_block = True

            for idx in range(a_len):
                code_point = _get_code_point(a, idx)
                is_whitespace = _is_whitespace(code_point)
                if in_whitespace_block:
                    if is_whitespace:
                        pass  # keep consuming space
                    else:
                        last = idx  # this is the start of the next string
                        in_whitespace_block = False
                else:
                    if not is_whitespace:
                        pass  # keep searching for whitespace transition
                    else:
                        parts.append(a[last:idx])
                        in_whitespace_block = True
                        split_count += 1
                        if maxsplit != -1 and split_count == maxsplit:
                            break

            if last <= a_len and not in_whitespace_block:
                parts.append(a[last:])

            return parts
        return split_whitespace_impl