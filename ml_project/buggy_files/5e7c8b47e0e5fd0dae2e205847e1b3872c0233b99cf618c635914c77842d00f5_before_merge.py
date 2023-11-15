    def workspace_status(self):
        current_checksum = self._get_checksum(locked=True)
        updated_checksum = self._get_checksum(locked=False)

        if current_checksum != updated_checksum:
            return {str(self): "update available"}

        return {}