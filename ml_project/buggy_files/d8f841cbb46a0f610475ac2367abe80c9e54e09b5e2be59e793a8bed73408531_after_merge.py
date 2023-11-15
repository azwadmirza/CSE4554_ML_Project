    def _abbreviate(self, s, n=5):
        s = utf8text(s)
        if len(s) > n:
            return s[:n] + '...'
        return s