    def do_class_init(cls):
        """
        Register attribute implementation.
        """
        from numba.targets.imputils import lower_getattr
        attr = cls._attr

        @lower_getattr(cls.key, attr)
        def getattr_impl(context, builder, typ, value):
            typingctx = context.typing_context
            fnty = cls._get_function_type(typingctx, typ)
            sig = cls._get_signature(typingctx, fnty, (typ,), {})
            call = context.get_function(fnty, sig)
            return call(builder, (value,))