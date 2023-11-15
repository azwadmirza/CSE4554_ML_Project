        def method_impl(context, builder, sig, args):
            typ = sig.args[0]
            typing_context = context.typing_context
            fnty = cls._get_function_type(typing_context, typ)
            sig = cls._get_signature(typing_context, fnty, sig.args, {})
            call = context.get_function(fnty, sig)
            # Link dependent library
            context.add_linking_libs(getattr(call, 'libs', ()))
            return call(builder, args)