    def __str__(self) -> str:
        return f"There is already a package named {self.spec.name.split('.')[-1]} loaded"