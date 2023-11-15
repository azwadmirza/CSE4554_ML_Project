    def to_json(self):
        data_path = data_manager.cog_data_path()
        return {
            "location": self._location.relative_to(data_path).parts
        }