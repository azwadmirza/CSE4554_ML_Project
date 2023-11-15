    def workspace_status(self):
        current = self._get_hash(locked=True)
        updated = self._get_hash(locked=False)

        if current != updated:
            return {str(self): "update available"}

        return {}