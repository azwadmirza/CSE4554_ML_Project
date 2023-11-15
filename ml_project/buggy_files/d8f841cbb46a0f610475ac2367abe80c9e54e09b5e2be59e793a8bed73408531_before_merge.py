    def _abbreviate(self, s, n=5):
        if len(s) > n:
            return s[:n] + '...'
        return s