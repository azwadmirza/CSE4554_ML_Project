    def res(*args, **kwargs):
        mem = get_mem(args)
        var_list = [_normalize_arg(_, mem) for _ in args]
        if 'out' in kwargs:
            var_list.append(_normalize_arg.pop('out'))
        if kwargs:
            raise TypeError('Wrong arguments %s' % kwargs)
        assert nin <= len(var_list) and len(var_list) <= nin + nout
        in_vars = var_list[:nin]
        out_vars = var_list[nin:]
        can_cast = can_cast1 if _should_use_min_scalar(in_vars) else can_cast2
        for ty_ins, ty_outs, op in ufunc._ops:
            ty_ins = [numpy.dtype(_) for _ in ty_ins]
            ty_outs = [numpy.dtype(_) for _ in ty_outs]
            if can_cast(in_vars, ty_ins):
                param_names = (['in%d' % i for i in six.moves.range(nin)] +
                               ['out%d' % i for i in six.moves.range(nout)])
                ret = []
                for i in six.moves.range(nout):
                    if i >= len(out_vars):
                        v = mem.get_fresh(ty_outs[i])
                        out_vars.append(v)
                        ret.append(_FusionRef(v, mem))
                    elif numpy.can_cast(ty_outs[i], out_vars[i].ty,
                                        "same_kind"):
                        v = out_vars[i]
                        ret.append(_FusionRef(v, mem))
                    else:
                        raise TypeError("Cannot cast from %s to %s"
                                        % (ty_outs[i], out_vars[i].ty)
                                        + " with casting rule 'same_kind'")
                mem.set_op(ufunc.name, op, param_names, nin, nout,
                           in_vars, out_vars, ty_ins + ty_outs)
                return ret[0] if len(ret) == 1 else tuple(ret)
        raise TypeError('Invalid type cast in \'{}\': {} -> {}'.format(
            ufunc.name,
            [_.ty for _ in in_vars],
            [_.ty for _ in out_vars]))