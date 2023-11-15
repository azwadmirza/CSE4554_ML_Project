def unicode_charseq_ljust(a, width, fillchar=' '):
    if isinstance(a, types.UnicodeCharSeq):
        if fillchar == ' ':
            def impl(a, width):
                return str(a).ljust(width)
            return impl
        elif isinstance(fillchar, types.UnicodeCharSeq):
            def impl(a, width, fillchar):
                return str(a).ljust(width, str(fillchar))
            return impl
        elif isinstance(fillchar, types.UnicodeType):
            def impl(a, width, fillchar):
                return str(a).ljust(width, fillchar)
            return impl
    if isinstance(a, (types.CharSeq, types.Bytes)):
        if fillchar == ' ' or fillchar == b' ':
            def impl(a, width):
                return a._to_str().ljust(width)._to_bytes()
            return impl
        elif isinstance(fillchar, (types.CharSeq, types.Bytes)):
            def impl(a, width, fillchar):
                return a._to_str().ljust(width, fillchar._to_str())._to_bytes()
            return impl