    def slice_size(self, index, dsize, equiv_set, scope, stmts):
        """Reason about the size of a slice represented by the "index"
        variable, and return a variable that has this size data, or
        raise GuardException if it cannot reason about it.

        The computation takes care of negative values used in the slice
        with respect to the given dimensional size ("dsize").

        Extra statments required to produce the result are appended
        to parent function's stmts list.
        """
        loc = index.loc
        # Get the definition of the index variable.
        index_def = get_definition(self.func_ir, index)
        fname, mod_name = find_callname(
            self.func_ir, index_def, typemap=self.typemap)
        require(fname == 'slice' and mod_name in ('__builtin__', 'builtins'))
        require(len(index_def.args) == 2)
        lhs = index_def.args[0]
        rhs = index_def.args[1]
        size_typ = self.typemap[dsize.name]
        lhs_typ = self.typemap[lhs.name]
        rhs_typ = self.typemap[rhs.name]

        if config.DEBUG_ARRAY_OPT >= 2:
            print("slice_size", "index", index, "dsize", dsize,
                  "index_def", index_def, "lhs", lhs, "rhs", rhs,
                  "size_typ", size_typ, "lhs_typ", lhs_typ, "rhs_typ", rhs_typ)

        # Fill in the left side of the slice's ":" with 0 if it wasn't specified.
        if isinstance(lhs_typ, types.NoneType):
            zero_var = ir.Var(scope, mk_unique_var("zero"), loc)
            zero = ir.Const(0, loc)
            stmts.append(ir.Assign(value=zero, target=zero_var, loc=loc))
            self._define(equiv_set, zero_var, types.IntegerLiteral(0), zero)
            lhs = zero_var
            lhs_typ = types.IntegerLiteral(0)

        # Fill in the right side of the slice's ":" with the array
        # length if it wasn't specified.
        if isinstance(rhs_typ, types.NoneType):
            rhs = dsize
            rhs_typ = size_typ

        lhs_rel = equiv_set.get_rel(lhs)
        rhs_rel = equiv_set.get_rel(rhs)
        if config.DEBUG_ARRAY_OPT >= 2:
            print("lhs_rel", lhs_rel, "rhs_rel", rhs_rel)

        # Make a deepcopy of the original slice to use as the
        # replacement slice, which we will modify as necessary
        # below to convert all negative constants in the slice
        # to be relative to the dimension size.
        replacement_slice = copy.deepcopy(index_def)
        need_replacement = False

        # If the first part of the slice is a constant N then check if N
        # is negative.  If so, then rewrite the first part of the slice
        # to be "dsize - N".  This is necessary because later steps will
        # try to compute slice size with a subtraction which wouldn't work
        # if any part of the slice was negative.
        if isinstance(lhs_rel, int):
            if lhs_rel < 0:
                # Indicate we will need to replace the slice var.
                need_replacement = True
                explicit_neg_var, explicit_neg_typ = self.gen_explicit_neg(lhs,
                    lhs_rel, lhs_typ, size_typ, loc, scope, dsize, stmts, equiv_set)
                replacement_slice.args = (explicit_neg_var, rhs)
                # Update lhs information with the negative removed.
                lhs = replacement_slice.args[0]
                lhs_typ = explicit_neg_typ
                lhs_rel = equiv_set.get_rel(lhs)

        # If the second part of the slice is a constant N then check if N
        # is negative.  If so, then rewrite the second part of the slice
        # to be "dsize - N".  This is necessary because later steps will
        # try to compute slice size with a subtraction which wouldn't work
        # if any part of the slice was negative.
        if isinstance(rhs_rel, int):
            if rhs_rel < 0:
                # Indicate we will need to replace the slice var.
                need_replacement = True
                explicit_neg_var, explicit_neg_typ = self.gen_explicit_neg(rhs,
                    rhs_rel, rhs_typ, size_typ, loc, scope, dsize, stmts, equiv_set)
                replacement_slice.args = (lhs, explicit_neg_var)
                # Update rhs information with the negative removed.
                rhs = replacement_slice.args[1]
                rhs_typ = explicit_neg_typ
                rhs_rel = equiv_set.get_rel(rhs)

        # If neither of the parts of the slice were negative constants
        # then we don't need to do slice replacement in the IR.
        if not need_replacement:
            replacement_slice_var = None
        else:
            # Create a new var for the replacement slice.
            replacement_slice_var = ir.Var(scope, mk_unique_var("replacement_slice"), loc)
            # Create a deepcopy of slice calltype so that when we change it below
            # the original isn't changed.  Make the types of the parts of the slice
            # intp.
            new_arg_typs = (types.intp, types.intp)
            rs_calltype = self.typemap[index_def.func.name].get_call_type(self.context, new_arg_typs, {})
            self.calltypes[replacement_slice] = rs_calltype
            stmts.append(ir.Assign(value=replacement_slice, target=replacement_slice_var, loc=loc))
            # The type of the replacement slice is the same type as the original.
            self.typemap[replacement_slice_var.name] = self.typemap[index.name]

        if config.DEBUG_ARRAY_OPT >= 2:
            print("after rewriting negatives", "lhs_rel", lhs_rel, "rhs_rel", rhs_rel)

        if (lhs_rel == 0 and isinstance(rhs_rel, tuple) and
            equiv_set.is_equiv(dsize, rhs_rel[0]) and
            rhs_rel[1] == 0):
            return dsize, None

        slice_typ = types.intp

        size_var = ir.Var(scope, mk_unique_var("slice_size"), loc)
        size_val = ir.Expr.binop(operator.sub, rhs, lhs, loc=loc)
        self.calltypes[size_val] = signature(slice_typ, rhs_typ, lhs_typ)
        self._define(equiv_set, size_var, slice_typ, size_val)

        # short cut size_val to a constant if its relation is known to be
        # a constant
        size_rel = equiv_set.get_rel(size_var)
        if config.DEBUG_ARRAY_OPT >= 2:
            print("size_var", size_var, "size_val", size_val, "size_rel", size_rel)
        if (isinstance(size_rel, int)):
            size_val = ir.Const(size_rel, loc=loc)
            size_var = ir.Var(scope, mk_unique_var("slice_size"), loc)
            slice_typ = types.IntegerLiteral(size_rel)
            self._define(equiv_set, size_var, slice_typ, size_val)
            if config.DEBUG_ARRAY_OPT >= 2:
                print("inferred constant size", "size_var", size_var, "size_val", size_val)

        # rel_map keeps a map of relative sizes that we have seen so
        # that if we compute the same relative sizes different times
        # in different ways we can associate those two instances
        # of the same relative size to the same equivalence class.
        if isinstance(size_rel, tuple):
            if config.DEBUG_ARRAY_OPT >= 2:
                print("size_rel is tuple", size_rel in equiv_set.rel_map)
            if size_rel in equiv_set.rel_map:
                # We have seen this relative size before so establish
                # equivalence to the previous variable.
                if config.DEBUG_ARRAY_OPT >= 2:
                    print("establishing equivalence to", equiv_set.rel_map[size_rel])
                equiv_set.insert_equiv(size_var, equiv_set.rel_map[size_rel])
            else:
                # The first time we've seen this relative size so
                # remember the variable defining that size.
                equiv_set.rel_map[size_rel] = size_var

        wrap_var = ir.Var(scope, mk_unique_var("wrap"), loc)
        wrap_def = ir.Global('wrap_index', wrap_index, loc=loc)
        fnty = get_global_func_typ(wrap_index)
        sig = self.context.resolve_function_type(fnty, (slice_typ, size_typ,), {})
        self._define(equiv_set, wrap_var, fnty, wrap_def)

        var = ir.Var(scope, mk_unique_var("var"), loc)
        value = ir.Expr.call(wrap_var, [size_var, dsize], {}, loc)
        self._define(equiv_set, var, slice_typ, value)
        self.calltypes[value] = sig

        stmts.append(ir.Assign(value=size_val, target=size_var, loc=loc))
        stmts.append(ir.Assign(value=wrap_def, target=wrap_var, loc=loc))
        stmts.append(ir.Assign(value=value, target=var, loc=loc))
        return var, replacement_slice_var