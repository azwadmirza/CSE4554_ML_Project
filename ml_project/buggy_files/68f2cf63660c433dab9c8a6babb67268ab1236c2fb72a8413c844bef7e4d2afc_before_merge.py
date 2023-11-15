    def to_json(self):
        return {
            "url": self.url,
            "name": self.name,
            "branch": self.branch,
            "folder_path": self.folder_path.relative_to(Path.cwd()).parts,
            "available_modules": [m.to_json() for m in self.available_modules]
        }