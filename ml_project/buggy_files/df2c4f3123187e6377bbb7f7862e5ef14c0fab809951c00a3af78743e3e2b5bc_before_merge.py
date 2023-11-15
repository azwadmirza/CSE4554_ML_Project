    def _index_name(self, col):
        if col.startswith("__index__"):
            return None
        return col