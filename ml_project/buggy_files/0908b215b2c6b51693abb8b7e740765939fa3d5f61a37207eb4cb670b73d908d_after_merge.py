    def inline_closure_call(self, block, i, callee):
        """Inline the body of `callee` at its callsite (`i`-th instruction of `block`)
        """
        scope = block.scope
        instr = block.body[i]
        call_expr = instr.value
        debug_print = _make_debug_print("inline_closure_call")
        debug_print("Found closure call: ", instr, " with callee = ", callee)
        func_ir = self.func_ir
        # first, get the IR of the callee
        callee_ir = self.get_ir_of_code(callee.code)
        callee_blocks = callee_ir.blocks

        # 1. relabel callee_ir by adding an offset
        max_label = max(func_ir.blocks.keys())
        callee_blocks = add_offset_to_labels(callee_blocks, max_label + 1)
        callee_ir.blocks = callee_blocks
        min_label = min(callee_blocks.keys())
        max_label = max(callee_blocks.keys())
        #    reset globals in ir_utils before we use it
        ir_utils._max_label = max_label
        debug_print("After relabel")
        _debug_dump(callee_ir)

        # 2. rename all local variables in callee_ir with new locals created in func_ir
        callee_scopes = _get_all_scopes(callee_blocks)
        debug_print("callee_scopes = ", callee_scopes)
        #    one function should only have one local scope
        assert(len(callee_scopes) == 1)
        callee_scope = callee_scopes[0]
        var_dict = {}
        for var in callee_scope.localvars._con.values():
            if not (var.name in callee.code.co_freevars):
                new_var = scope.define(mk_unique_var(var.name), loc=var.loc)
                var_dict[var.name] = new_var
        debug_print("var_dict = ", var_dict)
        replace_vars(callee_blocks, var_dict)
        debug_print("After local var rename")
        _debug_dump(callee_ir)

        # 3. replace formal parameters with actual arguments
        args = list(call_expr.args)
        if callee.defaults:
            debug_print("defaults = ", callee.defaults)
            if isinstance(callee.defaults, tuple): # Python 3.5
                args = args + list(callee.defaults)
            elif isinstance(callee.defaults, ir.Var) or isinstance(callee.defaults, str):
                defaults = func_ir.get_definition(callee.defaults)
                assert(isinstance(defaults, ir.Const))
                loc = defaults.loc
                args = args + [ir.Const(value=v, loc=loc)
                               for v in defaults.value]
            else:
                raise NotImplementedError(
                    "Unsupported defaults to make_function: {}".format(defaults))
        _replace_args_with(callee_blocks, args)
        debug_print("After arguments rename: ")
        _debug_dump(callee_ir)

        # 4. replace freevar with actual closure var
        if callee.closure:
            closure = func_ir.get_definition(callee.closure)
            assert(isinstance(closure, ir.Expr)
                   and closure.op == 'build_tuple')
            assert(len(callee.code.co_freevars) == len(closure.items))
            debug_print("callee's closure = ", closure)
            _replace_freevars(callee_blocks, closure.items)
            debug_print("After closure rename")
            _debug_dump(callee_ir)

        # 5. split caller blocks into two
        new_blocks = []
        new_block = ir.Block(scope, block.loc)
        new_block.body = block.body[i + 1:]
        new_label = next_label()
        func_ir.blocks[new_label] = new_block
        new_blocks.append((new_label, new_block))
        block.body = block.body[:i]
        block.body.append(ir.Jump(min_label, instr.loc))

        # 6. replace Return with assignment to LHS
        topo_order = find_topo_order(callee_blocks)
        _replace_returns(callee_blocks, instr.target, new_label)
        #    remove the old definition of instr.target too
        if (instr.target.name in func_ir._definitions):
            func_ir._definitions[instr.target.name] = []

        # 7. insert all new blocks, and add back definitions
        for label in topo_order:
            # block scope must point to parent's
            block = callee_blocks[label]
            block.scope = scope
            _add_definitions(func_ir, block)
            func_ir.blocks[label] = block
            new_blocks.append((label, block))
        debug_print("After merge in")
        _debug_dump(func_ir)

        return new_blocks