    def _run_inliner(
        self, state, inline_type, sig, template, arg_typs, expr, i, impl, block,
        work_list, is_method,
    ):
        from numba.core.inline_closurecall import (inline_closure_call,
                                                   callee_ir_validator)

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
            # pass is typed so use the callee globals
            inline_closure_call(state.func_ir, impl.__globals__,
                                block, i, impl, typingctx=state.typingctx,
                                arg_typs=arg_typs,
                                typemap=state.type_annotation.typemap,
                                calltypes=state.type_annotation.calltypes,
                                work_list=work_list,
                                replace_freevars=False,
                                callee_validator=callee_ir_validator)
            return True
        else:
            return False