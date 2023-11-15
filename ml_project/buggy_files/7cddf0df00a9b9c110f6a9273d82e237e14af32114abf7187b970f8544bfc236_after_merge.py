    def copy(self):
        new_ir = copy.copy(self)
        new_ir.blocks = self.blocks.copy()
        return new_ir