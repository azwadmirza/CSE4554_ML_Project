    def from_json(cls, payload):
        data = json.loads(payload)
        data["version_info"] = VersionInfo(**data["version_info"])  # restore this to a named tuple structure
        result = cls()
        for var in vars(result):
            setattr(result, var, data[var])
        return result