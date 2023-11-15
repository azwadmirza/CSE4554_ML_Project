def unicode_charseq_center(a, width, fillchar=' '):
    if isinstance(a, types.UnicodeCharSeq):
        if is_default(fillchar, ' '):
            def impl(a, width, fillchar=' '):
                return str(a).center(width)
            return impl
        elif isinstance(fillchar, types.UnicodeCharSeq):
            def impl(a, width, fillchar=' '):
                return str(a).center(width, str(fillchar))
            return impl
        elif isinstance(fillchar, types.UnicodeType):
            def impl(a, width, fillchar=' '):
                return str(a).center(width, fillchar)
            return impl
    if isinstance(a, (types.CharSeq, types.Bytes)):
        if is_default(fillchar, ' ') or is_default(fillchar, b' '):
            def impl(a, width, fillchar=' '):
                return a._to_str().center(width)._to_bytes()
            return impl
        elif isinstance(fillchar, (types.CharSeq, types.Bytes)):
            def impl(a, width, fillchar=' '):
                return a._to_str().center(width, fillchar._to_str())._to_bytes()
            return impl