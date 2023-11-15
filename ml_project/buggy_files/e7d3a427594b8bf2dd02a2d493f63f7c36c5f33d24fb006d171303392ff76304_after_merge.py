    def add_success(self, name: str, example: Case) -> None:
        self.checks.append(Check(name, Status.success, example))