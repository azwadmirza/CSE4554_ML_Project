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
            if not a.is_precise():
                # Getitem on non-precise array is allowed to
                # support array-comprehension
                if fnty == 'getitem' and isinstance(pos_args[0], types.Array):
                    pass
                # Otherwise, don't compute type yet
                else:
                    return

        # Resolve call type
        sig = typeinfer.resolve_call(fnty, pos_args, kw_args)
        if sig is None:
            # Arguments are invalid => explain why
            headtemp = "Invalid usage of {0} with parameters ({1})"
            args = [str(a) for a in pos_args]
            args += ["%s=%s" % (k, v) for k, v in sorted(kw_args.items())]
            head = headtemp.format(fnty, ', '.join(map(str, args)))
            desc = context.explain_function_type(fnty)
            msg = '\n'.join([head, desc])
            raise TypingError(msg, loc=self.loc)

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

        target_type = typevars[self.target].getone()
        if isinstance(target_type, types.Array) and isinstance(sig.return_type.dtype, types.Undefined):
            typeinfer.refine_map[self.target] = self