    def to_json(self):
        return {
            "location": self._location.relative_to(Path.cwd()).parts
        }