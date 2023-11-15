    def environment(self):
        dependencies = []
        with open(self.filename) as reqfile:
            for line in reqfile:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                dependencies.append(line)
        return env.Environment(
            name=self.name,
            dependencies=dependencies
        )