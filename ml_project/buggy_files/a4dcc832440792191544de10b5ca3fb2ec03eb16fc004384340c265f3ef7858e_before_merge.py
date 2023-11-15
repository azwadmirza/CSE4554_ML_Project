    def _do_work_getattr(self, state, work_list, block, i, expr):
        recv_type = state.type_annotation.typemap[expr.value.name]
        recv_type = types.unliteral(recv_type)
        matched = state.typingctx.find_matching_getattr_template(
            recv_type, expr.attr,
        )
        if not matched:
            return False
        template = matched['template']
        if getattr(template, 'is_method', False):
            # The attribute template is representing a method.
            # Don't inline the getattr.
            return False

        inline_type = getattr(template, '_inline', None)
        if inline_type is None:
            # inline not defined
            return False
        sig = typing.signature(matched['return_type'], recv_type)
        arg_typs = sig.args

        if not inline_type.is_never_inline:
            try:
                impl = template._overload_func(recv_type)
                if impl is None:
                    raise Exception  # abort for this template
            except Exception:
                return False
        else:
            return False

        is_method = False
        return self._run_inliner(
            state, inline_type, sig, template, arg_typs, expr, i, impl, block,
            work_list, is_method,
        )