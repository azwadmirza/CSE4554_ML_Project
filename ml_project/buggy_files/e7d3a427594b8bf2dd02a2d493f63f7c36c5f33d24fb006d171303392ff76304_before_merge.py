    def add_success(self, name: str) -> None:
        self.checks.append(Check(name, Status.success))