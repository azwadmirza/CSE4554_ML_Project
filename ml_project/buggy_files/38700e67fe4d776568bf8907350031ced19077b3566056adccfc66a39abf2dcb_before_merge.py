    def resolve(self, typeinfer, typevars, fnty):
        assert fnty
        context = typeinfer.context

        r = fold_arg_vars(typevars, self.args, self.vararg, self.kws)
        if r is None:
            # Cannot resolve call type until all argument types are known
            return
        pos_args, kw_args = r

        # Check argument to be precise
        for a in itertools.chain(pos_args, kw_args.values()):
            # Forbids imprecise type except array of undefined dtype
            if not a.is_precise() and not isinstance(a, types.Array):
                return

        # Resolve call type
        try:
            sig = typeinfer.resolve_call(fnty, pos_args, kw_args)
        except ForceLiteralArg as e:
            folded = e.fold_arguments(self.args, self.kws)
            requested = set()
            unsatisified = set()
            for idx in e.requested_args:
                maybe_arg = typeinfer.func_ir.get_definition(folded[idx])
                if isinstance(maybe_arg, ir.Arg):
                    requested.add(maybe_arg.index)
                else:
                    unsatisified.add(idx)
            if unsatisified:
                raise TypingError("Cannot request literal type.", loc=self.loc)
            elif requested:
                raise ForceLiteralArg(requested, loc=self.loc)
        if sig is None:
            # Note: duplicated error checking.
            #       See types.BaseFunction.get_call_type
            # Arguments are invalid => explain why
            headtemp = "Invalid use of {0} with parameters ({1})"
            args = [str(a) for a in pos_args]
            args += ["%s=%s" % (k, v) for k, v in sorted(kw_args.items())]
            head = headtemp.format(fnty, ', '.join(map(str, args)))
            desc = context.explain_function_type(fnty)
            msg = '\n'.join([head, desc])
            raise TypingError(msg)

        typeinfer.add_type(self.target, sig.return_type, loc=self.loc)

        # If the function is a bound function and its receiver type
        # was refined, propagate it.
        if (isinstance(fnty, types.BoundFunction)
                and sig.recvr is not None
                and sig.recvr != fnty.this):
            refined_this = context.unify_pairs(sig.recvr, fnty.this)
            if refined_this is not None and refined_this.is_precise():
                refined_fnty = fnty.copy(this=refined_this)
                typeinfer.propagate_refined_type(self.func, refined_fnty)

        # If the return type is imprecise but can be unified with the
        # target variable's inferred type, use the latter.
        # Useful for code such as::
        #    s = set()
        #    s.add(1)
        # (the set() call must be typed as int64(), not undefined())
        if not sig.return_type.is_precise():
            target = typevars[self.target]
            if target.defined:
                targetty = target.getone()
                if context.unify_pairs(targetty, sig.return_type) == targetty:
                    sig = sig.replace(return_type=targetty)

        self.signature = sig
        self._add_refine_map(typeinfer, typevars, sig)