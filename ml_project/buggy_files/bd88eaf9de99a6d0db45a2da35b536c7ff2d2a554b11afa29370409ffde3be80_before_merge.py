def unicode_count(src, sub, start=None, end=None):

    _count_args_types_check(start)
    _count_args_types_check(end)

    if isinstance(sub, types.UnicodeType):
        def count_impl(src, sub, start=start, end=end):
            count = 0
            src_len = len(src)
            sub_len = len(sub)

            start = _normalize_slice_idx_count(start, src_len, 0)
            end = _normalize_slice_idx_count(end, src_len, src_len)

            if end - start < 0 or start > src_len:
                return 0

            src = src[start : end]
            src_len = len(src)
            start, end = 0, src_len
            if sub_len == 0:
                return src_len + 1

            while(start + sub_len <= src_len):
                if src[start : start + sub_len] == sub:
                    count += 1
                    start += sub_len
                else:
                    start += 1
            return count
        return count_impl
    error_msg = "The substring must be a UnicodeType, not {}"
    raise TypingError(error_msg.format(type(sub)))