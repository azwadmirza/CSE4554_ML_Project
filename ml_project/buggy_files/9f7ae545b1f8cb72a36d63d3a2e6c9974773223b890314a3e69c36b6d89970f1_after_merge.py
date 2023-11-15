    def visit_type_type(self, t: TypeType) -> None:
        t.item.accept(self)