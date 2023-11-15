    def u(s, errors='replace'):
        if isinstance(s, text_type):
            return s
        return s.decode('utf-8', errors=errors)