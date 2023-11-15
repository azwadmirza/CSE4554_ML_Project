    def _get_len(self, var):
        """Return sequence length"""
        try:
            return len(var)
        except TypeError:
            return None