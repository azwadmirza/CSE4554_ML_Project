    def from_json(cls, data: dict):
        location = Path.cwd() / Path(*data["location"])
        return cls(location=location)