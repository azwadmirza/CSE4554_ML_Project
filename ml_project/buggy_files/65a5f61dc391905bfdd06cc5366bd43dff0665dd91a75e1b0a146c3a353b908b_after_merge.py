    def parse(cls, version_string):
        if version_string.lower() in cls.LNAMES:
            return cls.from_name(version_string)
        match = cls.git_describe_regex.match(version_string)
        if not match:
            raise ValueError(
                'Unable to parse version string: {0!r}'.format(version_string)
            )
        return cls(*match.groups())