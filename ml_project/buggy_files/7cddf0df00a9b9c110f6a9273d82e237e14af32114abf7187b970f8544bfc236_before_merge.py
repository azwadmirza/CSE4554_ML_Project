    def copy(self):
        block = Block(self.scope, self.loc)
        block.body = self.body[:]
        return block