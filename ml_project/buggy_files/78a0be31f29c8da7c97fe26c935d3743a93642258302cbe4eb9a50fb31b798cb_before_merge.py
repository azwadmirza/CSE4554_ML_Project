    def typeof_expr(self, inst, target, expr):
        if expr.op == 'call':
            if isinstance(expr.func, ir.Intrinsic):
                sig = expr.func.type
                self.add_type(target.name, sig.return_type, loc=inst.loc)
                self.add_calltype(expr, sig)
            else:
                self.typeof_call(inst, target, expr)
        elif expr.op in ('getiter', 'iternext'):
            self.typeof_intrinsic_call(inst, target, expr.op, expr.value)
        elif expr.op == 'exhaust_iter':
            constraint = ExhaustIterConstraint(target.name, count=expr.count,
                                               iterator=expr.value,
                                               loc=expr.loc)
            self.constraints.append(constraint)
        elif expr.op == 'pair_first':
            constraint = PairFirstConstraint(target.name, pair=expr.value,
                                             loc=expr.loc)
            self.constraints.append(constraint)
        elif expr.op == 'pair_second':
            constraint = PairSecondConstraint(target.name, pair=expr.value,
                                              loc=expr.loc)
            self.constraints.append(constraint)
        elif expr.op == 'binop':
            self.typeof_intrinsic_call(inst, target, expr.fn, expr.lhs,
                                       expr.rhs)
        elif expr.op == 'inplace_binop':
            self.typeof_intrinsic_call(inst, target, expr.fn,
                                       expr.lhs, expr.rhs)
        elif expr.op == 'unary':
            self.typeof_intrinsic_call(inst, target, expr.fn, expr.value)
        elif expr.op == 'static_getitem':
            constraint = StaticGetItemConstraint(target.name, value=expr.value,
                                                 index=expr.index,
                                                 index_var=expr.index_var,
                                                 loc=expr.loc)
            self.constraints.append(constraint)
            self.calls.append((inst.value, constraint))
        elif expr.op == 'getitem':
            self.typeof_intrinsic_call(inst, target, operator.getitem,
                                       expr.value, expr.index,)
        elif expr.op == 'typed_getitem':
            constraint = TypedGetItemConstraint(target.name, value=expr.value,
                                                dtype=expr.dtype,
                                                index=expr.index,
                                                loc=expr.loc)
            self.constraints.append(constraint)
            self.calls.append((inst.value, constraint))

        elif expr.op == 'getattr':
            constraint = GetAttrConstraint(target.name, attr=expr.attr,
                                           value=expr.value, loc=inst.loc,
                                           inst=inst)
            self.constraints.append(constraint)
        elif expr.op == 'build_tuple':
            constraint = BuildTupleConstraint(target.name, items=expr.items,
                                              loc=inst.loc)
            self.constraints.append(constraint)
        elif expr.op == 'build_list':
            constraint = BuildListConstraint(target.name, items=expr.items,
                                             loc=inst.loc)
            self.constraints.append(constraint)
        elif expr.op == 'build_set':
            constraint = BuildSetConstraint(target.name, items=expr.items,
                                            loc=inst.loc)
            self.constraints.append(constraint)
        elif expr.op == 'build_map':
            constraint = BuildMapConstraint(
                target.name,
                items=expr.items,
                special_value=expr.literal_value,
                value_indexes=expr.value_indexes,
                loc=inst.loc)
            self.constraints.append(constraint)
        elif expr.op == 'cast':
            self.constraints.append(Propagate(dst=target.name,
                                              src=expr.value.name,
                                              loc=inst.loc))
        elif expr.op == 'phi':
            for iv in expr.incoming_values:
                if iv is not ir.UNDEFINED:
                    self.constraints.append(Propagate(dst=target.name,
                                                      src=iv.name,
                                                      loc=inst.loc))
        elif expr.op == 'make_function':
            self.lock_type(target.name, types.MakeFunctionLiteral(expr),
                           loc=inst.loc, literal_value=expr)
        else:
            msg = "Unsupported op-code encountered: %s" % expr
            raise UnsupportedError(msg, loc=inst.loc)