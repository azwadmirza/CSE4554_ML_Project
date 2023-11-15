    def match(self, func_ir, block, typemap, calltypes):
        """
        Using typing and a basic block, search the basic block for array
        expressions.
        Return True when one or more matches were found, False otherwise.
        """
        # We can trivially reject everything if there are no
        # calls in the type results.
        if len(calltypes) == 0:
            return False

        self.crnt_block = block
        self.typemap = typemap
        # { variable name: IR assignment (of a function call or operator) }
        self.array_assigns = OrderedDict()
        # { variable name: IR assignment (of a constant) }
        self.const_assigns = {}

        assignments = block.find_insts(ir.Assign)
        for instr in assignments:
            target_name = instr.target.name
            expr = instr.value
            # Does it assign an expression to an array variable?
            if (isinstance(expr, ir.Expr) and
                isinstance(typemap.get(target_name, None), types.Array)):
                self._match_array_expr(instr, expr, target_name)
            elif isinstance(expr, ir.Const):
                # Track constants since we might need them for an
                # array expression.
                self.const_assigns[target_name] = expr

        return len(self.array_assigns) > 0