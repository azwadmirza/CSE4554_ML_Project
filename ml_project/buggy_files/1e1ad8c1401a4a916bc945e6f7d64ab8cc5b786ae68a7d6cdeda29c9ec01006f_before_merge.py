    def visit_block(self, b: Block) -> Type:
        if b.is_unreachable:
            return None
        for s in b.body:
            self.accept(s)
            if self.binder.breaking_out:
                break