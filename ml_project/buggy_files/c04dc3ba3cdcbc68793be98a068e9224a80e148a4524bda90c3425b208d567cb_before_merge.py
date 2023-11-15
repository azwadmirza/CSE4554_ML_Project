def unicode_find(data, substr, start=None, end=None):
    """Implements str.find()"""
    if isinstance(substr, types.UnicodeCharSeq):
        def find_impl(data, substr):
            return data.find(str(substr))
        return find_impl

    unicode_idx_check_type(start, 'start')
    unicode_idx_check_type(end, 'end')
    unicode_sub_check_type(substr, 'substr')

    return _find