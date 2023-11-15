    def inline_closure_call(self, block, i, callee):
        """Inline the body of `callee` at its callsite (`i`-th instruction of `block`)
        """
        scope = block.scope
        instr = block.body[i]
        call_expr = instr.value
        _debug_print("Found closure call: ", instr, " with callee = ", callee)
        func_ir = self.func_ir
        # first, get the IR of the callee
        from_ir = self.get_ir_of_code(callee.code)
        from_blocks = from_ir.blocks
        # 1. relabel from_ir by adding an offset
        max_label = max(func_ir.blocks.keys())
        from_blocks = add_offset_to_labels(from_blocks, max_label + 1)
        from_ir.blocks = from_blocks
        min_label = min(from_blocks.keys())
        max_label = max(from_blocks.keys())
        #    reset globals in ir_utils before we use it
        ir_utils._max_label = max_label 
        ir_utils.visit_vars_extensions = {}
        # 2. rename all local variables in from_ir with new locals created in func_ir
        from_scopes = _get_all_scopes(from_blocks)
        _debug_print("obj_IR has scopes: ", from_scopes)
        #    one function should only have one local scope
        assert(len(from_scopes) == 1)
        from_scope = from_scopes[0]
        var_dict = {}
        for var in from_scope.localvars._con.values():
            if not (var.name in callee.code.co_freevars):
                var_dict[var.name] = scope.make_temp(var.loc)
        _debug_print("Before local var rename: var_dict = ", var_dict)
        _debug_dump(from_ir)
        replace_vars(from_blocks, var_dict)
        _debug_print("After local var rename: ")
        _debug_dump(from_ir)
        # 3. replace formal parameters with actual arguments
        args = list(call_expr.args)
        if callee.defaults:
            _debug_print("defaults", callee.defaults)
            if isinstance(callee.defaults, tuple): # Python 3.5
                args = args + list(callee.defaults)
            elif isinstance(callee.defaults, ir.Var) or isinstance(callee.defaults, str):
                defaults = func_ir.get_definition(callee.defaults)
                assert(isinstance(defaults, ir.Const))
                loc = defaults.loc
                args = args + [ ir.Const(value=v, loc=loc) for v in defaults.value ]
            else:
                raise NotImplementedError("Unsupported defaults to make_function: {}".format(defaults))
        _replace_args_with(from_blocks, args)
        _debug_print("After arguments rename: ")
        _debug_dump(from_ir)
        # 4. replace freevar with actual closure var
        if callee.closure:
            closure = func_ir.get_definition(callee.closure)
            assert(isinstance(closure, ir.Expr) and closure.op == 'build_tuple')
            assert(len(callee.code.co_freevars) == len(closure.items))
            _debug_print("callee's closure = ", closure)
            _replace_freevars(from_blocks, closure.items)
            _debug_print("After closure rename: ")
            _debug_dump(from_ir)
        # 5. split caller blocks into two
        new_blocks = []
        new_block = ir.Block(scope, block.loc)
        new_block.body = block.body[i+1:]
        new_label = next_label()
        func_ir.blocks[new_label] = new_block
        new_blocks.append((new_label, new_block))
        block.body = block.body[:i]
        block.body.append(ir.Jump(min_label, instr.loc))
        # 6. replace Return with assignment to LHS
        _replace_returns(from_blocks, instr.target, new_label)
        # 7. insert all new blocks, and add back definitions
        for label, block in from_blocks.items():
            # block scope must point to parent's
            block.scope = scope
            _add_definition(func_ir, block)
            func_ir.blocks[label] = block
            new_blocks.append((label, block))
        _debug_print("After merge: ")
        _debug_dump(func_ir)
        return new_blocks