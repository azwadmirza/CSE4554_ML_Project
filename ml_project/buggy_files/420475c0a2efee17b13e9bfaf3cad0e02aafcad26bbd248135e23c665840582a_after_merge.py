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
            print("slice_size", "index=", index, "dsize=", dsize,
                  "index_def=", index_def, "lhs=", lhs, "rhs=", rhs,
                  "size_typ=", size_typ, "lhs_typ=", lhs_typ, "rhs_typ=", rhs_typ)

        # Make a deepcopy of the original slice to use as the
        # replacement slice, which we will modify as necessary
        # below to convert all negative constants in the slice
        # to be relative to the dimension size.
        replacement_slice = copy.deepcopy(index_def)
        need_replacement = False

        # Fill in the left side of the slice's ":" with 0 if it wasn't specified.
        if isinstance(lhs_typ, types.NoneType):
            zero_var = ir.Var(scope, mk_unique_var("zero"), loc)
            zero = ir.Const(0, loc)
            stmts.append(ir.Assign(value=zero, target=zero_var, loc=loc))
            self._define(equiv_set, zero_var, types.IntegerLiteral(0), zero)
            lhs = zero_var
            lhs_typ = types.IntegerLiteral(0)
            replacement_slice.args = (lhs, replacement_slice.args[1])
            need_replacement = True
            if config.DEBUG_ARRAY_OPT >= 2:
                print("Replacing slice because lhs is None.")

        # Fill in the right side of the slice's ":" with the array
        # length if it wasn't specified.
        if isinstance(rhs_typ, types.NoneType):
            rhs = dsize
            rhs_typ = size_typ
            replacement_slice.args = (replacement_slice.args[0], rhs)
            need_replacement = True
            if config.DEBUG_ARRAY_OPT >= 2:
                print("Replacing slice because lhs is None.")

        lhs_rel = equiv_set.get_rel(lhs)
        rhs_rel = equiv_set.get_rel(rhs)
        dsize_rel = equiv_set.get_rel(dsize)
        if config.DEBUG_ARRAY_OPT >= 2:
            print("lhs_rel", lhs_rel, "rhs_rel", rhs_rel, "dsize_rel", dsize_rel)

        # Update replacement slice with the real index value if we can
        # compute it at compile time.
        lhs, lhs_typ, lhs_rel, replacement_slice, need_replacement, lhs_known = self.update_replacement_slice(
              lhs, lhs_typ, lhs_rel, dsize_rel, replacement_slice, 0,
              need_replacement, loc, scope, stmts, equiv_set, size_typ, dsize)
        rhs, rhs_typ, rhs_rel, replacement_slice, need_replacement, rhs_known = self.update_replacement_slice(
              rhs, rhs_typ, rhs_rel, dsize_rel, replacement_slice, 1,
              need_replacement, loc, scope, stmts, equiv_set, size_typ, dsize)
        if config.DEBUG_ARRAY_OPT >= 2:
            print("lhs_known:", lhs_known)
            print("rhs_known:", rhs_known)

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

        if lhs_known and rhs_known:
            if config.DEBUG_ARRAY_OPT >= 2:
                print("lhs and rhs known so return static size")
            return self.gen_static_slice_size(lhs_rel, rhs_rel, loc, scope, stmts, equiv_set), replacement_slice_var

        if (lhs_rel == 0 and isinstance(rhs_rel, tuple) and
            equiv_set.is_equiv(dsize, rhs_rel[0]) and
            rhs_rel[1] == 0):
            return dsize, None

        slice_typ = types.intp
        orig_slice_typ = slice_typ

        size_var = ir.Var(scope, mk_unique_var("slice_size"), loc)
        size_val = ir.Expr.binop(operator.sub, rhs, lhs, loc=loc)
        self.calltypes[size_val] = signature(slice_typ, rhs_typ, lhs_typ)
        self._define(equiv_set, size_var, slice_typ, size_val)
        size_rel = equiv_set.get_rel(size_var)
        if config.DEBUG_ARRAY_OPT >= 2:
            print("size_rel", size_rel, type(size_rel))

        wrap_var = ir.Var(scope, mk_unique_var("wrap"), loc)
        wrap_def = ir.Global('wrap_index', wrap_index, loc=loc)
        fnty = get_global_func_typ(wrap_index)
        sig = self.context.resolve_function_type(fnty, (orig_slice_typ, size_typ,), {})
        self._define(equiv_set, wrap_var, fnty, wrap_def)

        def gen_wrap_if_not_known(val, val_typ, known):
            if not known:
                var = ir.Var(scope, mk_unique_var("var"), loc)
                var_typ = types.intp
                new_value = ir.Expr.call(wrap_var, [val, dsize], {}, loc)
                self._define(equiv_set, var, var_typ, new_value)
                self.calltypes[new_value] = sig
                return (var, var_typ, new_value)
            else:
                return (val, val_typ, None)

        var1, var1_typ, value1 = gen_wrap_if_not_known(lhs, lhs_typ, lhs_known)
        var2, var2_typ, value2 = gen_wrap_if_not_known(rhs, rhs_typ, rhs_known)

        post_wrap_size_var = ir.Var(scope, mk_unique_var("post_wrap_slice_size"), loc)
        post_wrap_size_val = ir.Expr.binop(operator.sub, var2, var1, loc=loc)
        self.calltypes[post_wrap_size_val] = signature(slice_typ, var2_typ, var1_typ)
        self._define(equiv_set, post_wrap_size_var, slice_typ, post_wrap_size_val)

        stmts.append(ir.Assign(value=size_val, target=size_var, loc=loc))
        stmts.append(ir.Assign(value=wrap_def, target=wrap_var, loc=loc))
        if value1 is not None:
            stmts.append(ir.Assign(value=value1, target=var1, loc=loc))
        if value2 is not None:
            stmts.append(ir.Assign(value=value2, target=var2, loc=loc))
        stmts.append(ir.Assign(value=post_wrap_size_val, target=post_wrap_size_var, loc=loc))

        # rel_map keeps a map of relative sizes that we have seen so
        # that if we compute the same relative sizes different times
        # in different ways we can associate those two instances
        # of the same relative size to the same equivalence class.
        if isinstance(size_rel, tuple):
            if config.DEBUG_ARRAY_OPT >= 2:
                print("size_rel is tuple", equiv_set.rel_map)
            rel_map_entry = None
            for rme, rme_tuple in equiv_set.rel_map.items():
                if rme[1] == size_rel[1] and equiv_set.is_equiv(rme[0], size_rel[0]):
                    rel_map_entry = rme_tuple
                    break

            if rel_map_entry is not None:
                # We have seen this relative size before so establish
                # equivalence to the previous variable.
                if config.DEBUG_ARRAY_OPT >= 2:
                    print("establishing equivalence to", rel_map_entry)
                equiv_set.insert_equiv(size_var, rel_map_entry[0])
                equiv_set.insert_equiv(post_wrap_size_var, rel_map_entry[1])
            else:
                # The first time we've seen this relative size so
                # remember the variable defining that size.
                equiv_set.rel_map[size_rel] = (size_var, post_wrap_size_var)

        return post_wrap_size_var, replacement_slice_var