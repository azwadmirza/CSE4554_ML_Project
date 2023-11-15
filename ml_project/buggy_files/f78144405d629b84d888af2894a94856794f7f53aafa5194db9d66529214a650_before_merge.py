    def ustrftime(format, *args):
        # if a locale is set, the time strings are encoded in the encoding
        # given by LC_TIME; if that is available, use it
        enc = locale.getlocale(locale.LC_TIME)[1] or 'utf-8'
        return time.strftime(text_type(format).encode(enc), *args).decode(enc)