    def num_violations(self):
        """Count the number of violations in the path."""
        return sum(file.num_violations() for file in self.files)