    def replace_return_with_setitem(self, blocks, index_vars, out_name):
        """
        Find return statements in the IR and replace them with a SetItem
        call of the value "returned" by the kernel into the result array.
        Returns the block labels that contained return statements.
        """
        ret_blocks = []

        for label, block in blocks.items():
            scope = block.scope
            loc = block.loc
            new_body = []
            for stmt in block.body:
                if isinstance(stmt, ir.Return):
                    ret_blocks.append(label)
                    # If 1D array then avoid the tuple construction.
                    if len(index_vars) == 1:
                        rvar = ir.Var(scope, out_name, loc)
                        ivar = ir.Var(scope, index_vars[0], loc)
                        new_body.append(ir.SetItem(rvar, ivar, stmt.value, loc))
                    else:
                        # Convert the string names of the index variables into
                        # ir.Var's.
                        var_index_vars = []
                        for one_var in index_vars:
                            index_var = ir.Var(scope, one_var, loc)
                            var_index_vars += [index_var]

                        s_index_name = ir_utils.mk_unique_var("stencil_index")
                        s_index_var  = ir.Var(scope, s_index_name, loc)
                        # Build a tuple from the index ir.Var's.
                        tuple_call = ir.Expr.build_tuple(var_index_vars, loc)
                        new_body.append(ir.Assign(tuple_call, s_index_var, loc))
                        rvar = ir.Var(scope, out_name, loc)
                        # Write the return statements original value into
                        # the array using the tuple index.
                        si = ir.SetItem(rvar, s_index_var, stmt.value, loc)
                        new_body.append(si)
                else:
                    new_body.append(stmt)
            block.body = new_body
        return ret_blocks