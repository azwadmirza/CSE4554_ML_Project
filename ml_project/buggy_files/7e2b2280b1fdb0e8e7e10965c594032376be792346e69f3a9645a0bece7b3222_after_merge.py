    def generic(self, args, kws):
        assert not kws
        if len(args) == 1:
            # One-argument type() -> return the __class__
            # Avoid literal types
            arg = types.unliteral(args[0])
            classty = self.context.resolve_getattr(arg, "__class__")
            if classty is not None:
                return signature(classty, *args)