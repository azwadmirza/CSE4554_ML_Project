    def lower_expr(self, resty, expr):
        if expr.op == 'binop':
            return self.lower_binop(resty, expr, expr.fn)
        elif expr.op == 'inplace_binop':
            lty = self.typeof(expr.lhs.name)
            if lty.mutable:
                return self.lower_binop(resty, expr, expr.fn)
            else:
                # inplace operators on non-mutable types reuse the same
                # definition as the corresponding copying operators.)
                return self.lower_binop(resty, expr, expr.immutable_fn)
        elif expr.op == 'unary':
            val = self.loadvar(expr.value.name)
            typ = self.typeof(expr.value.name)
            func_ty = self.context.typing_context.resolve_value_type(expr.fn)
            # Get function
            signature = self.fndesc.calltypes[expr]
            impl = self.context.get_function(func_ty, signature)
            # Convert argument to match
            val = self.context.cast(self.builder, val, typ, signature.args[0])
            res = impl(self.builder, [val])
            res = self.context.cast(self.builder, res,
                                    signature.return_type, resty)
            return res

        elif expr.op == 'call':
            res = self.lower_call(resty, expr)
            return res

        elif expr.op == 'pair_first':
            val = self.loadvar(expr.value.name)
            ty = self.typeof(expr.value.name)
            res = self.context.pair_first(self.builder, val, ty)
            self.incref(resty, res)
            return res

        elif expr.op == 'pair_second':
            val = self.loadvar(expr.value.name)
            ty = self.typeof(expr.value.name)
            res = self.context.pair_second(self.builder, val, ty)
            self.incref(resty, res)
            return res

        elif expr.op in ('getiter', 'iternext'):
            val = self.loadvar(expr.value.name)
            ty = self.typeof(expr.value.name)
            signature = self.fndesc.calltypes[expr]
            impl = self.context.get_function(expr.op, signature)
            [fty] = signature.args
            castval = self.context.cast(self.builder, val, ty, fty)
            res = impl(self.builder, (castval,))
            res = self.context.cast(self.builder, res, signature.return_type,
                                    resty)
            return res

        elif expr.op == 'exhaust_iter':
            val = self.loadvar(expr.value.name)
            ty = self.typeof(expr.value.name)
            # Unpack optional
            if isinstance(ty, types.Optional):
                val = self.context.cast(self.builder, val, ty, ty.type)
                ty = ty.type

            # If we have a tuple, we needn't do anything
            # (and we can't iterate over the heterogeneous ones).
            if isinstance(ty, types.BaseTuple):
                assert ty == resty
                self.incref(ty, val)
                return val

            itemty = ty.iterator_type.yield_type
            tup = self.context.get_constant_undef(resty)
            pairty = types.Pair(itemty, types.boolean)
            getiter_sig = typing.signature(ty.iterator_type, ty)
            getiter_impl = self.context.get_function('getiter',
                                                     getiter_sig)
            iternext_sig = typing.signature(pairty, ty.iterator_type)
            iternext_impl = self.context.get_function('iternext',
                                                      iternext_sig)
            iterobj = getiter_impl(self.builder, (val,))
            # We call iternext() as many times as desired (`expr.count`).
            for i in range(expr.count):
                pair = iternext_impl(self.builder, (iterobj,))
                is_valid = self.context.pair_second(self.builder,
                                                    pair, pairty)
                with cgutils.if_unlikely(self.builder,
                                         self.builder.not_(is_valid)):
                    self.return_exception(ValueError, loc=self.loc)
                item = self.context.pair_first(self.builder,
                                               pair, pairty)
                tup = self.builder.insert_value(tup, item, i)

            # Call iternext() once more to check that the iterator
            # is exhausted.
            pair = iternext_impl(self.builder, (iterobj,))
            is_valid = self.context.pair_second(self.builder,
                                                pair, pairty)
            with cgutils.if_unlikely(self.builder, is_valid):
                self.return_exception(ValueError, loc=self.loc)

            self.decref(ty.iterator_type, iterobj)
            return tup

        elif expr.op == "getattr":
            val = self.loadvar(expr.value.name)
            ty = self.typeof(expr.value.name)

            if isinstance(resty, types.BoundFunction):
                # if we are getting out a method, assume we have typed this
                # properly and just build a bound function object
                casted = self.context.cast(self.builder, val, ty, resty.this)
                res = self.context.get_bound_function(self.builder, casted,
                                                      resty.this)
                self.incref(resty, res)
                return res
            else:
                impl = self.context.get_getattr(ty, expr.attr)
                attrty = self.context.typing_context.resolve_getattr(ty,
                                                                     expr.attr)

                if impl is None:
                    # ignore the attribute
                    return self.context.get_dummy_value()
                else:
                    res = impl(self.context, self.builder, ty, val, expr.attr)

                # Cast the attribute type to the expected output type
                res = self.context.cast(self.builder, res, attrty, resty)
                return res

        elif expr.op == "static_getitem":
            signature = typing.signature(
                resty,
                self.typeof(expr.value.name),
                _lit_or_omitted(expr.index),
            )
            try:
                # Both get_function() and the returned implementation can
                # raise NotImplementedError if the types aren't supported
                impl = self.context.get_function("static_getitem", signature)
                return impl(self.builder,
                            (self.loadvar(expr.value.name), expr.index))
            except NotImplementedError:
                if expr.index_var is None:
                    raise
                # Fall back on the generic getitem() implementation
                # for this type.
                signature = self.fndesc.calltypes[expr]
                return self.lower_getitem(resty, expr, expr.value,
                                          expr.index_var, signature)
        elif expr.op == "typed_getitem":
            signature = typing.signature(
                resty,
                self.typeof(expr.value.name),
                self.typeof(expr.index.name),
            )
            impl = self.context.get_function("typed_getitem", signature)
            return impl(self.builder, (self.loadvar(expr.value.name),
                        self.loadvar(expr.index.name)))
        elif expr.op == "getitem":
            signature = self.fndesc.calltypes[expr]
            return self.lower_getitem(resty, expr, expr.value, expr.index,
                                      signature)

        elif expr.op == "build_tuple":
            itemvals = [self.loadvar(i.name) for i in expr.items]
            itemtys = [self.typeof(i.name) for i in expr.items]
            castvals = [self.context.cast(self.builder, val, fromty, toty)
                        for val, toty, fromty in zip(itemvals, resty, itemtys)]
            tup = self.context.make_tuple(self.builder, resty, castvals)
            self.incref(resty, tup)
            return tup

        elif expr.op == "build_list":
            itemvals = [self.loadvar(i.name) for i in expr.items]
            itemtys = [self.typeof(i.name) for i in expr.items]
            castvals = [self.context.cast(self.builder, val, fromty,
                                          resty.dtype)
                        for val, fromty in zip(itemvals, itemtys)]
            return self.context.build_list(self.builder, resty, castvals)

        elif expr.op == "build_set":
            # Insert in reverse order, as Python does
            items = expr.items[::-1]
            itemvals = [self.loadvar(i.name) for i in items]
            itemtys = [self.typeof(i.name) for i in items]
            castvals = [self.context.cast(self.builder, val, fromty,
                                          resty.dtype)
                        for val, fromty in zip(itemvals, itemtys)]
            return self.context.build_set(self.builder, resty, castvals)

        elif expr.op == "build_map":
            items = expr.items
            keys, values = [], []
            key_types, value_types = [], []
            for k, v in items:
                key = self.loadvar(k.name)
                keytype = self.typeof(k.name)
                val = self.loadvar(v.name)
                valtype = self.typeof(v.name)
                keys.append(key)
                values.append(val)
                key_types.append(keytype)
                value_types.append(valtype)
            return self.context.build_map(self.builder, resty,
                                          list(zip(key_types, value_types)),
                                          list(zip(keys, values)))

        elif expr.op == "cast":
            val = self.loadvar(expr.value.name)
            ty = self.typeof(expr.value.name)
            castval = self.context.cast(self.builder, val, ty, resty)
            self.incref(resty, castval)
            return castval

        elif expr.op == "phi":
            raise LoweringError("PHI not stripped")

        elif expr.op == 'null':
            return self.context.get_constant_null(resty)

        elif expr.op in self.context.special_ops:
            res = self.context.special_ops[expr.op](self, expr)
            return res

        raise NotImplementedError(expr)