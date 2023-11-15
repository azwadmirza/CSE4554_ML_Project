    def last_valid_index(self):
        if len(self) == 0:
            return None

        valid_indices = self._get_valid_indices()
        return valid_indices[-1] if len(valid_indices) else None