    def nativestr(s):
        if isinstance(s, binary_type):
            return s
        return s.encode('utf-8', 'replace')