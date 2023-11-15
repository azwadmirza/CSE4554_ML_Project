    def find_simple(self, seen):
        types = oset.OrderedSet()
        for type in self.types:
            if type.is_promotion:
                types.add(type.types)
            else:
                type.add(type)

        return types