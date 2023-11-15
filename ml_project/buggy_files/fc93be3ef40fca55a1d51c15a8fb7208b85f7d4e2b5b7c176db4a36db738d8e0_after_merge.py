    def from_json(cls, payload):
        data = json.loads(payload)
        data["version_info"] = VersionInfo(**data["version_info"])  # restore this to a named tuple structure
        result = cls()
        result.__dict__ = {k: v for k, v in data.items()}
        return result