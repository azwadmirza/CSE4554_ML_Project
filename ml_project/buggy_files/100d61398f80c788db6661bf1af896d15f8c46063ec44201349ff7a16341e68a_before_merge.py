    def center_impl(string, width, fillchar=' '):
        str_len = len(string)
        fillchar_len = len(fillchar)

        if fillchar_len != 1:
            raise ValueError('The fill character must be exactly one character long')

        if width <= str_len:
            return string

        allmargin = width - str_len
        lmargin = (allmargin // 2) + (allmargin & width & 1)
        rmargin = allmargin - lmargin

        l_string = fillchar * lmargin
        if lmargin == rmargin:
            return l_string + string + l_string
        else:
            return l_string + string + (fillchar * rmargin)