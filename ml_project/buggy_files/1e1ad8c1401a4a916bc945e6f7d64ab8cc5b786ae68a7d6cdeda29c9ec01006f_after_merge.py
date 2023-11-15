    def visit_block(self, b: Block) -> Type:
        if b.is_unreachable:
            return None
        for s in b.body:
            if self.binder.is_unreachable():
                break
            self.accept(s)