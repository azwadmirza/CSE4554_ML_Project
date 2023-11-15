    def convert(self, path, value):
        for rexp in self.map.keys():
            if rexp.match(path):
                try:
                    return self.map[rexp](value)
                except ValueError as e:
                    raise ConfigurationError(
                        'Error while attempting to convert {} to appropriate type: {}'.format(
                            path, e
                        )
                    )
        return value