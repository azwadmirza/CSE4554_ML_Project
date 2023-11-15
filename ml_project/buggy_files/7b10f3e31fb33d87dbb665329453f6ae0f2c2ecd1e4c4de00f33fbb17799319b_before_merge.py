def unicode_rfind(data, substr, start=None, end=None):
    """Implements str.rfind()"""
    if isinstance(substr, types.UnicodeCharSeq):
        def rfind_impl(data, substr):
            return data.rfind(str(substr))
        return rfind_impl

    unicode_idx_check_type(start, 'start')
    unicode_idx_check_type(end, 'end')
    unicode_sub_check_type(substr, 'substr')

    return _rfind