def _PyUnicode_IsAlpha(ch):
    ctype = _PyUnicode_gettyperecord(ch)
    return ctype.flags & _PyUnicode_TyperecordMasks.ALPHA_MASK != 0