    def _make_assert_equiv(self, scope, loc, equiv_set, _args, names=None):
        # filter out those that are already equivalent
        if names == None:
            names = [x.name for x in _args]
        args = []
        arg_names = []
        for name, x in zip(names, _args):
            seen = False
            for y in args:
                if equiv_set.is_equiv(x, y):
                    seen = True
                    break
            if not seen:
                args.append(x)
                arg_names.append(name)

        # no assertion necessary if there are less than two
        if len(args) < 2:
            return []

        msg = "Sizes of {} do not match on {}".format(', '.join(arg_names), loc)
        msg_val = ir.Const(msg, loc)
        msg_typ = types.StringLiteral(msg)
        msg_var = ir.Var(scope, mk_unique_var("msg"), loc)
        self.typemap[msg_var.name] = msg_typ
        argtyps = tuple([msg_typ] + [self.typemap[x.name] for x in args])

        # assert_equiv takes vararg, which requires a tuple as argument type
        tup_typ = types.BaseTuple.from_types(argtyps)

        # prepare function variable whose type may vary since it takes vararg
        assert_var = ir.Var(scope, mk_unique_var("assert"), loc)
        assert_def = ir.Global('assert_equiv', assert_equiv, loc=loc)
        fnty = get_global_func_typ(assert_equiv)
        sig = self.context.resolve_function_type(fnty, (tup_typ,), {})
        self._define(equiv_set, assert_var, fnty, assert_def)

        # The return value from assert_equiv is always of none type.
        var = ir.Var(scope, mk_unique_var("ret"), loc)
        value = ir.Expr.call(assert_var, [msg_var] + args, {}, loc=loc)
        self._define(equiv_set, var, types.none, value)
        self.calltypes[value] = sig

        return [ir.Assign(value=msg_val, target=msg_var, loc=loc),
                ir.Assign(value=assert_def, target=assert_var, loc=loc),
                ir.Assign(value=value, target=var, loc=loc),
                ]