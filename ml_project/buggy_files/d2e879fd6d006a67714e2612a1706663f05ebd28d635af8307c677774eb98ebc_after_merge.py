    def lower_expr(self, expr):
        if expr.op == 'binop':
            return self.lower_binop(expr, expr.fn, inplace=False)
        elif expr.op == 'inplace_binop':
            return self.lower_binop(expr, expr.fn, inplace=True)
        elif expr.op == 'unary':
            value = self.loadvar(expr.value.name)
            if expr.fn == operator.neg:
                res = self.pyapi.number_negative(value)
            elif expr.fn == operator.pos:
                res = self.pyapi.number_positive(value)
            elif expr.fn == operator.not_:
                res = self.pyapi.object_not(value)
                self.check_int_status(res)

                longval = self.builder.zext(res, self.pyapi.long)
                res = self.pyapi.bool_from_long(longval)
            elif expr.fn == operator.invert:
                res = self.pyapi.number_invert(value)
            else:
                raise NotImplementedError(expr)
            self.check_error(res)
            return res
        elif expr.op == 'call':
            argvals = [self.loadvar(a.name) for a in expr.args]
            fn = self.loadvar(expr.func.name)
            args = self.pyapi.tuple_pack(argvals)
            if expr.vararg:
                # Expand *args
                new_args = self.pyapi.number_add(args,
                                                 self.loadvar(expr.vararg.name))
                self.decref(args)
                args = new_args
            if not expr.kws:
                # No named arguments
                ret = self.pyapi.call(fn, args, None)
            else:
                # Named arguments
                keyvalues = [(k, self.loadvar(v.name)) for k, v in expr.kws]
                kws = self.pyapi.dict_pack(keyvalues)
                ret = self.pyapi.call(fn, args, kws)
                self.decref(kws)
            self.decref(args)
            self.check_error(ret)
            return ret
        elif expr.op == 'getattr':
            obj = self.loadvar(expr.value.name)
            res = self.pyapi.object_getattr(obj, self._freeze_string(expr.attr))
            self.check_error(res)
            return res
        elif expr.op == 'build_tuple':
            items = [self.loadvar(it.name) for it in expr.items]
            res = self.pyapi.tuple_pack(items)
            self.check_error(res)
            return res
        elif expr.op == 'build_list':
            items = [self.loadvar(it.name) for it in expr.items]
            res = self.pyapi.list_pack(items)
            self.check_error(res)
            return res
        elif expr.op == 'build_map':
            res = self.pyapi.dict_new(expr.size)
            self.check_error(res)
            for k, v in expr.items:
                key = self.loadvar(k.name)
                value = self.loadvar(v.name)
                ok = self.pyapi.dict_setitem(res, key, value)
                self.check_int_status(ok)
            return res
        elif expr.op == 'build_set':
            items = [self.loadvar(it.name) for it in expr.items]
            res = self.pyapi.set_new()
            self.check_error(res)
            for it in items:
                ok = self.pyapi.set_add(res, it)
                self.check_int_status(ok)
            return res
        elif expr.op == 'getiter':
            obj = self.loadvar(expr.value.name)
            res = self.pyapi.object_getiter(obj)
            self.check_error(res)
            return res
        elif expr.op == 'iternext':
            iterobj = self.loadvar(expr.value.name)
            item = self.pyapi.iter_next(iterobj)
            is_valid = cgutils.is_not_null(self.builder, item)
            pair = self.pyapi.tuple_new(2)
            with self.builder.if_else(is_valid) as (then, otherwise):
                with then:
                    self.pyapi.tuple_setitem(pair, 0, item)
                with otherwise:
                    self.check_occurred()
                    # Make the tuple valid by inserting None as dummy
                    # iteration "result" (it will be ignored).
                    self.pyapi.tuple_setitem(pair, 0, self.pyapi.make_none())
            self.pyapi.tuple_setitem(pair, 1, self.pyapi.bool_from_bool(is_valid))
            return pair
        elif expr.op == 'pair_first':
            pair = self.loadvar(expr.value.name)
            first = self.pyapi.tuple_getitem(pair, 0)
            self.incref(first)
            return first
        elif expr.op == 'pair_second':
            pair = self.loadvar(expr.value.name)
            second = self.pyapi.tuple_getitem(pair, 1)
            self.incref(second)
            return second
        elif expr.op == 'exhaust_iter':
            iterobj = self.loadvar(expr.value.name)
            tup = self.pyapi.sequence_tuple(iterobj)
            self.check_error(tup)
            # Check tuple size is as expected
            tup_size = self.pyapi.tuple_size(tup)
            expected_size = self.context.get_constant(types.intp, expr.count)
            has_wrong_size = self.builder.icmp(lc.ICMP_NE,
                                               tup_size, expected_size)
            with cgutils.if_unlikely(self.builder, has_wrong_size):
                self.return_exception(ValueError)
            return tup
        elif expr.op == 'getitem':
            value = self.loadvar(expr.value.name)
            index = self.loadvar(expr.index.name)
            res = self.pyapi.object_getitem(value, index)
            self.check_error(res)
            return res
        elif expr.op == 'static_getitem':
            value = self.loadvar(expr.value.name)
            index = self.context.get_constant(types.intp, expr.index)
            indexobj = self.pyapi.long_from_ssize_t(index)
            self.check_error(indexobj)
            res = self.pyapi.object_getitem(value, indexobj)
            self.decref(indexobj)
            self.check_error(res)
            return res
        elif expr.op == 'getslice':
            target = self.loadvar(expr.target.name)
            start = self.loadvar(expr.start.name)
            stop = self.loadvar(expr.stop.name)

            slicefn = self.get_builtin_obj("slice")
            sliceobj = self.pyapi.call_function_objargs(slicefn, (start, stop))
            self.decref(slicefn)
            self.check_error(sliceobj)

            res = self.pyapi.object_getitem(target, sliceobj)
            self.check_error(res)

            return res

        elif expr.op == 'cast':
            val = self.loadvar(expr.value.name)
            self.incref(val)
            return val
        elif expr.op == 'phi':
            raise LoweringError("PHI not stripped")

        elif expr.op == 'null':
            # Make null value
            return cgutils.get_null_value(self.pyapi.pyobj)

        else:
            raise NotImplementedError(expr)