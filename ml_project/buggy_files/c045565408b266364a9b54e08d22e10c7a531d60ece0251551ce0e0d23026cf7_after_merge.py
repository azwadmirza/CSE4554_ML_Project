    def _get_len(self, var):
        """Return sequence length"""
        try:
            return len(var)
        except:
            return None