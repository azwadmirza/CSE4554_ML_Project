    def entities_resolver(self, root, info, representations):
        results = []

        for representation in representations:
            type_name = representation.pop("__typename")
            type = self.type_map[type_name]

            results.append(type.definition.origin.resolve_reference(**representation))

        return results