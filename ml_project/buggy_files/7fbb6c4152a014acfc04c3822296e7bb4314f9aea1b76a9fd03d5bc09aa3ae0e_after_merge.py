def unicode_charseq_strip(a, chars=None):
    if isinstance(a, types.UnicodeCharSeq):
        if is_nonelike(chars):
            def impl(a, chars=None):
                return str(a).strip()
            return impl
        elif isinstance(chars, types.UnicodeCharSeq):
            def impl(a, chars=None):
                return str(a).strip(str(chars))
            return impl
        elif isinstance(chars, types.UnicodeType):
            def impl(a, chars=None):
                return str(a).strip(chars)
            return impl
    if isinstance(a, (types.CharSeq, types.Bytes)):
        if is_nonelike(chars):
            def impl(a, chars=None):
                return a._to_str().strip()._to_bytes()
            return impl
        elif isinstance(chars, (types.CharSeq, types.Bytes)):
            def impl(a, chars=None):
                return a._to_str().strip(chars._to_str())._to_bytes()
            return impl