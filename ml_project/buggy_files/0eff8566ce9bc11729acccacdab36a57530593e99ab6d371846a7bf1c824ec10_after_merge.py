    def from_json(cls, data: dict):
        data_path = data_manager.cog_data_path()
        location = data_path / Path(*data["location"])
        return cls(location=location)