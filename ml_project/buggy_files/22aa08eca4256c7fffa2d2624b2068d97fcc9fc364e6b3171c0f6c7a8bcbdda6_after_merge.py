    def u(s, errors='replace'):
        if isinstance(s, text_type):
            return s.encode('utf-8',errors=errors)
        return s.decode('utf-8', errors=errors)