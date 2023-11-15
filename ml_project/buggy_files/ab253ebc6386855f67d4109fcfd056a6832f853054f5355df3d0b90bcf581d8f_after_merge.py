    def num_violations(self, **kwargs):
        """Count the number of violations in thie result."""
        return sum(path.num_violations(**kwargs) for path in self.paths)