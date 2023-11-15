    def nativestr(s):
        if isinstance(s, binary_type):
            return s
        elif isinstance(s, (int, float)):
            return s.__str__()
        else:
            return s.encode('utf-8', 'replace')