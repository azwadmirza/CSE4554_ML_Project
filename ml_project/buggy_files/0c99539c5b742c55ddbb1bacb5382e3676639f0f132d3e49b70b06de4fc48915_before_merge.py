    def pipfile_part(self):
        pipfile_dict = attr.asdict(self, filter=_filter_none)
        if "version" not in pipfile_dict:
            pipfile_dict["version"] = "*"
        name = pipfile_dict.pop("name")
        return {name: pipfile_dict}