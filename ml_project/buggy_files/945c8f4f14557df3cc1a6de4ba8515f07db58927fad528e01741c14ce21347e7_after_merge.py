    def get_target_dependencies(self):
        deps = self.dependencies[:]
        deps += self.extra_depends
        for c in self.sources:
            if hasattr(c, 'held_object'):
                c = c.held_object
            if isinstance(c, (BuildTarget, CustomTarget)):
                deps.append(c)
        return deps