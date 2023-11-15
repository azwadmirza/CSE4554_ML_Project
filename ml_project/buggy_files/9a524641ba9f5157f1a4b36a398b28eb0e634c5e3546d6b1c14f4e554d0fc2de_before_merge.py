def _get_fusion(func, nin, reduce, post_map, identity, input_types, name=None):
    in_vars = [_FusionVar(i, t) for i, t in enumerate(input_types)]
    mem = _FusionMem(in_vars)
    in_refs = [_FusionRef(_, mem) for _ in in_vars]
    out_refs = func(*in_refs)
    out_refs = list(out_refs) if type(out_refs) == tuple else [out_refs]
    out_refs = filter(lambda i: i is not None, out_refs)
    out_refs = [_FusionRef(_normalize_arg(_, mem), mem) for _ in out_refs]
    out_vars = [_normalize_arg(copy(_), mem) for _ in out_refs]
    nout = len(out_vars)
    op_list = mem.op_list
    tmpvars = mem.var_list[nin:-nout] if nout > 0 else mem.var_list[nin:]

    in_params = ', '.join(_get_params(in_vars))
    out_params = ', '.join(_get_params(out_vars))
    operation = ''.join(_get_declaration_from_var(_) for _ in tmpvars)
    operation += ''.join(_get_declaration_from_op(_) for _ in op_list)
    operation += '\n'.join(_get_operation_code(_) for _ in op_list)

    if name is None:
        name = 'fusion__' + '__'.join(build_kernel_name(_) for _ in op_list)

    if reduce is None:
        if not out_params:
            in_params = ', '.join(_get_params(in_vars[:-1]))
            out_params = ', '.join(_get_params([in_vars[-1]]))
        submodules = _gather_submodules(op_list)
        submodule_code = ''.join(_get_submodule_code(_)
                                 for _ in submodules.values())
        return core.ElementwiseKernel(in_params, out_params,
                                      operation, preamble=submodule_code,
                                      name=name)
    else:
        if nout != 1:
            raise Exception("Wrong number of number of arguments")
        # pre-map
        pre_type = out_vars[0].ty
        pre_code = _get_pre_code(in_vars, out_vars, operation)

        # reduce
        reduce_op = _get_reduce_op(reduce._raw, pre_type)
        reduce_code = reduce_op[2][1]
        reduce_type = numpy.dtype(reduce_op[1][0])
        rtype = reduce_op[2][3]
        post_type = "type_in0_raw" if rtype is None else rtype
        pre_code += "typedef %s type_in0_raw;\n" % _dtype_to_ctype[reduce_type]

        # post-map
        post_in = [_FusionVar(0, reduce_type)]
        mem = _FusionMem(post_in)
        post_in_ref = [_FusionRef(_, mem) for _ in post_in]
        post_out = _normalize_arg(post_map(*post_in_ref), mem)
        if type(post_out) == tuple:
            raise Exception("Can't reduce a tuple")
        post_vars = mem.var_list
        post_ops = mem.op_list
        post_code = ''.join(_get_declaration_from_var(_)
                            for _ in post_vars[1:])
        post_code += ''.join(_get_declaration_from_op(_) for _ in post_ops)
        post_code += '\n'.join(_get_operation_code(_) for _ in post_ops)
        post_code = _get_post_code(post_vars, post_code, post_out)
        post_code += _get_fix_code(post_type, reduce_type, reduce_op[2][2])

        submodules = _gather_submodules(op_list + post_ops)
        submodule_code = ''.join(_get_submodule_code(v)
                                 for v in submodules.values())
        submodule_code += reduce._raw._preamble + pre_code + post_code
        operation_args = ['v' + str(i) for i in six.moves.range(nin)]
        operation = '_pre_map(' + ', '.join(operation_args) + ')'
        out_params = '%s res' % post_out.ty
        return core.ReductionKernel(in_params, out_params, operation,
                                    reduce_code,
                                    'res = _post_map(_post_fix(a))',
                                    identity,
                                    reduce_type=post_type,
                                    preamble=submodule_code)