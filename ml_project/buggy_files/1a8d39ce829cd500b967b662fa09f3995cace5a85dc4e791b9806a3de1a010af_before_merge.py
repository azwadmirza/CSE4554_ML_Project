def unicode_charseq_lstrip(a, chars=None):
    if isinstance(a, types.UnicodeCharSeq):
        if chars is None or isinstance(chars, types.NoneType):
            def impl(a):
                return str(a).lstrip()
            return impl
        elif isinstance(chars, types.UnicodeCharSeq):
            def impl(a, chars):
                return str(a).lstrip(str(chars))
            return impl
        elif isinstance(chars, types.UnicodeType):
            def impl(a, chars):
                return str(a).lstrip(chars)
            return impl
    if isinstance(a, (types.CharSeq, types.Bytes)):
        if chars is None or isinstance(chars, types.NoneType):
            def impl(a):
                return a._to_str().lstrip()._to_bytes()
            return impl
        elif isinstance(chars, (types.CharSeq, types.Bytes)):
            def impl(a, chars):
                return a._to_str().lstrip(chars._to_str())._to_bytes()
            return impl