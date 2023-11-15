        def method_impl(context, builder, sig, args):
            typ = sig.args[0]
            typing_context = context.typing_context
            disp = cls._get_dispatcher(typing_context, typ, attr, sig.args, {})
            disp_type = types.Dispatcher(disp)
            sig = disp_type.get_call_type(typing_context, sig.args, {})
            call = context.get_function(disp_type, sig)
            # Link dependent library
            context.add_linking_libs(getattr(call, 'libs', ()))
            return call(builder, args)