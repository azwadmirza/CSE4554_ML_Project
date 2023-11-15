    def ustrftime(format, *args):
        # On Windows, time.strftime() and Unicode characters will raise UnicodeEncodeError.
        # http://bugs.python.org/issue8304
        try:
            return time.strftime(format, *args)
        except UnicodeEncodeError:
            r = time.strftime(format.encode('unicode-escape').decode(), *args)
            return r.encode().decode('unicode-escape')