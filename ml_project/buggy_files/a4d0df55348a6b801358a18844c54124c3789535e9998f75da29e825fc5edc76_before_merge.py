        def get_safe(self, key, default=None, path=None, type_t=()):
            """
                Get values in format
            """
            path = path or []
            value = self.get(key, default)
            if not isinstance(value, (dict)):
                if isinstance(value, type_t) or not type_t:
                    return [(value, (path[:] + [key]))]

            results = []
            for sub_v, sub_path in value.items_safe(path + [key]):
                if isinstance(sub_v, type_t) or not type_t:
                    results.append((sub_v, sub_path))

            return results