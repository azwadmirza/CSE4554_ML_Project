    def num_violations(self):
        """Count the number of violations in thie result."""
        return sum(path.num_violations() for path in self.paths)