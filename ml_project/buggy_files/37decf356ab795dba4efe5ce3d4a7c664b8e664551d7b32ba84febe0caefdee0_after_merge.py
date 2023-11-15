def _PyUnicode_IsNumeric(ch):
    ctype = _PyUnicode_gettyperecord(ch)
    return ctype.flags & _PyUnicode_TyperecordMasks.NUMERIC_MASK != 0