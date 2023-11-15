    def do_class_init(cls):
        """
        Register generic method implementation.
        """
        from numba.targets.imputils import lower_builtin
        attr = cls._attr

        @lower_builtin((cls.key, attr), cls.key, types.VarArg(types.Any))
        def method_impl(context, builder, sig, args):
            typ = sig.args[0]
            typing_context = context.typing_context
            disp = cls._get_dispatcher(typing_context, typ, attr, sig.args, {})
            disp_type = types.Dispatcher(disp)
            sig = disp_type.get_call_type(typing_context, sig.args, {})
            call = context.get_function(disp_type, sig)
            # Link dependent library
            context.add_linking_libs(getattr(call, 'libs', ()))
            return call(builder, _adjust_omitted_args(sig.args, args))