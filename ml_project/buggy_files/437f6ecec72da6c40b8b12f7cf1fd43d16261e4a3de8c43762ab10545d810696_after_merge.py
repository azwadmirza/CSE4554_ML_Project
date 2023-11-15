    def visit_block(self, b: Block) -> None:
        if b.is_unreachable:
            return
        super().visit_block(b)