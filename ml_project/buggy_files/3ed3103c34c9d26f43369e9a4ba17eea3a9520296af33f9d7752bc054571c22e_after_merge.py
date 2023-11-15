def unicode_rjust(string, width, fillchar=' '):
    if not isinstance(width, types.Integer):
        raise TypingError('The width must be an Integer')

    if isinstance(fillchar, types.UnicodeCharSeq):
        def rjust_impl(string, width, fillchar):
            return string.rjust(width, str(fillchar))
        return rjust_impl

    if not (fillchar == ' ' or isinstance(fillchar, (types.Omitted, types.UnicodeType))):
        raise TypingError('The fillchar must be a UnicodeType')

    def rjust_impl(string, width, fillchar=' '):
        str_len = len(string)
        fillchar_len = len(fillchar)

        if fillchar_len != 1:
            raise ValueError('The fill character must be exactly one character long')

        if width <= str_len:
            return string

        newstr = (fillchar * (width - str_len)) + string

        return newstr
    return rjust_impl