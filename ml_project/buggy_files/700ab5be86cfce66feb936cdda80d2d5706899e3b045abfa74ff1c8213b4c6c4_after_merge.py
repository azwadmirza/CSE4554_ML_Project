    def find_types(self, seen):
        types = oset.OrderedSet([self])
        seen.add(self)
        seen.add(self.variable.deferred_type)
        self.dfs(types, seen)
        types.remove(self)
        return types