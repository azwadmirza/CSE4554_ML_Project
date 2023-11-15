    def rjust_impl(string, width, fillchar=' '):
        str_len = len(string)
        fillchar_len = len(fillchar)

        if fillchar_len != 1:
            raise ValueError('The fill character must be exactly one character long')

        if width <= str_len:
            return string

        newstr = (fillchar * (width - str_len)) + string

        return newstr