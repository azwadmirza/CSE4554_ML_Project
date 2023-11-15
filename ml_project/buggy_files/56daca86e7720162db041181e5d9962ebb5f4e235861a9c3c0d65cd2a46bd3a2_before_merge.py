    def match(self, func_ir, block, typemap, calltypes):
        """
        Detect all getitem expressions and find which ones have
        string literal indexes
        """
        self.getitems = getitems = {}
        self.block = block
        for expr in block.find_exprs(op='getitem'):
            if expr.op == 'getitem':
                index_ty = typemap[expr.index.name]
                if isinstance(index_ty, types.StringLiteral):
                    getitems[expr] = (expr.index, index_ty.literal_value)

        return len(getitems) > 0