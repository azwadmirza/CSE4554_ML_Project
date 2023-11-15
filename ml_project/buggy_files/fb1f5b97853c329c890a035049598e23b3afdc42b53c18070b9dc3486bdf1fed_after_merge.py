    def visit_type_application(self, e: TypeApplication) -> None:
        for type in e.types:
            self.analyze(type, e)
        super().visit_type_application(e)