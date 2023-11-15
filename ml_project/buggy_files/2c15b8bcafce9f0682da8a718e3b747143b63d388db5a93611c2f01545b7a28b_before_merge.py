    def set_path_value(config, path, value, prefix=()):
        # Postgresql GUCs can't be nested, but can contain dots so we re-flatten the structure for this case
        if prefix == ('postgresql', 'parameters'):
            path = ['.'.join(path)]

        if len(path) == 1:
            if value is None:
                config.pop(path[0], None)
            else:
                config[path[0]] = value
        else:
            key = path[0]
            if key not in config:
                config[key] = {}
            set_path_value(config[key], path[1:], value, prefix + (key,))
            if config[key] == {}:
                del config[key]