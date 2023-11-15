        def get_safe(self, key, default=None, path=None, type_t=()):
            """
                Get values in format
            """
            path = path or []
            value = self.get(key, default)
            if value is None and default is None:
                # if default is None and value is None return empty list
                return []

            # if the value is the default make sure that the default value is of type_t when specified
            if bool(type_t) and value == default and not isinstance(default, type_t):
                raise ValueError('"default" type should be of "type_t"')

            # when not a dict see if if the value is of the right type
            results = []
            if not isinstance(value, (dict)):
                if isinstance(value, type_t) or not type_t:
                    return [(value, (path[:] + [key]))]
            else:
                for sub_v, sub_path in value.items_safe(path + [key]):
                    if isinstance(sub_v, type_t) or not type_t:
                        results.append((sub_v, sub_path))

            return results