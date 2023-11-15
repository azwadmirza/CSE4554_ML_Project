        def getattr_impl(context, builder, typ, value):
            typingctx = context.typing_context
            fnty = cls._get_function_type(typingctx, typ)
            sig = cls._get_signature(typingctx, fnty, (typ,), {})
            call = context.get_function(fnty, sig)
            return call(builder, (value,))