    def is_ancestor(self, other):
        if isinstance(other, ir.Expr):
            other = other.op()

        if self.equals(other):
            return True

        table = self.table
        exist_layers = False
        op = table.op()
        while not (op.blocks() or isinstance(op, Join)):
            table = table.op().table
            exist_layers = True

        if exist_layers:
            reboxed = Selection(table, self.selections)
            return reboxed.is_ancestor(other)
        else:
            return False