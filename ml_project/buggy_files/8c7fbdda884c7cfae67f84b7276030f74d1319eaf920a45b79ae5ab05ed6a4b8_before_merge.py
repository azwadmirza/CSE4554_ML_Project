    def _do_work_call(self, state, work_list, block, i, expr):
        # try and get a definition for the call, this isn't always possible as
        # it might be a eval(str)/part generated awaiting update etc. (parfors)
        to_inline = None
        try:
            to_inline = state.func_ir.get_definition(expr.func)
        except Exception:
            return False

        # do not handle closure inlining here, another pass deals with that.
        if getattr(to_inline, 'op', False) == 'make_function':
            return False

        # check this is a known and typed function
        try:
            func_ty = state.type_annotation.typemap[expr.func.name]
        except KeyError:
            # e.g. Calls to CUDA Intrinsic have no mapped type so KeyError
            return False
        if not hasattr(func_ty, 'get_call_type'):
            return False

        sig = state.type_annotation.calltypes[expr]
        is_method = False

        # search the templates for this overload looking for "inline"
        if getattr(func_ty, 'template', None) is not None:
            # @overload_method
            is_method = True
            templates = [func_ty.template]
            arg_typs = (func_ty.template.this,) + sig.args
        else:
            # @overload case
            templates = getattr(func_ty, 'templates', None)
            arg_typs = sig.args

        if templates is None:
            return False

        impl = None
        for template in templates:
            inline_type = getattr(template, '_inline', None)
            if inline_type is None:
                # inline not defined
                continue
            if not inline_type.is_never_inline:
                try:
                    impl = template._overload_func(*arg_typs)
                    if impl is None:
                        raise Exception  # abort for this template
                    break
                except Exception:
                    continue
        else:
            return False

        # at this point we know we maybe want to inline something and there's
        # definitely something that could be inlined.
        return self._run_inliner(
            state, inline_type, sig, template, arg_typs, expr, i, impl, block,
            work_list, is_method,
        )