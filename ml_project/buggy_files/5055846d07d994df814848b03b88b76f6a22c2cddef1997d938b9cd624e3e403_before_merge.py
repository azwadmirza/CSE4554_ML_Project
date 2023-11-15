    def find_simple(self, seen):
        types = set()
        for type in self.types:
            if type.is_promotion:
                types.add(type.types)
            else:
                type.add(type)

        return types