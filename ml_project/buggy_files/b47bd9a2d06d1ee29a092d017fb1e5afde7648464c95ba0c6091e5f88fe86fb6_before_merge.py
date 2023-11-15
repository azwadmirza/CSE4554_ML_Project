    def environment(self):
        dependencies = []
        with open(self.filename) as reqfile:
            for line in reqfile:
                dependencies.append(line)
        return env.Environment(
            name=self.name,
            dependencies=dependencies
        )