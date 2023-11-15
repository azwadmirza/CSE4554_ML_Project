    def to_json(self):
        data_path = data_manager.cog_data_path()
        return {
            "url": self.url,
            "name": self.name,
            "branch": self.branch,
            "folder_path": self.folder_path.relative_to(data_path).parts,
            "available_modules": [m.to_json() for m in self.available_modules]
        }