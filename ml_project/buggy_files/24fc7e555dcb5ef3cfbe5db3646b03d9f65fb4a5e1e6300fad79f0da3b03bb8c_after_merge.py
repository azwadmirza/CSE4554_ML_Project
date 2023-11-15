def _PyUnicode_IsPrintable(ch):
    ctype = _PyUnicode_gettyperecord(ch)
    return ctype.flags & _PyUnicode_TyperecordMasks.PRINTABLE_MASK != 0