    def _run_inliner(
        self, state, inline_type, sig, template, arg_typs, expr, i, impl, block,
        work_list, is_method, inline_worker,
    ):

        do_inline = True
        if not inline_type.is_always_inline:
            from numba.core.typing.templates import _inline_info
            caller_inline_info = _inline_info(state.func_ir,
                                              state.type_annotation.typemap,
                                              state.type_annotation.calltypes,
                                              sig)

            # must be a cost-model function, run the function
            iinfo = template._inline_overloads[arg_typs]['iinfo']
            if inline_type.has_cost_model:
                do_inline = inline_type.value(expr, caller_inline_info, iinfo)
            else:
                assert 'unreachable'

        if do_inline:
            if is_method:
                if not self._add_method_self_arg(state, expr):
                    return False
            arg_typs = template._inline_overloads[arg_typs]['folded_args']
            iinfo = template._inline_overloads[arg_typs]['iinfo']
            freevars = iinfo.func_ir.func_id.func.__code__.co_freevars
            _, _, _, new_blocks = inline_worker.inline_ir(state.func_ir,
                                                          block,
                                                          i,
                                                          iinfo.func_ir,
                                                          freevars,
                                                          arg_typs=arg_typs)
            if work_list is not None:
                for blk in new_blocks:
                    work_list.append(blk)
            return True
        else:
            return False