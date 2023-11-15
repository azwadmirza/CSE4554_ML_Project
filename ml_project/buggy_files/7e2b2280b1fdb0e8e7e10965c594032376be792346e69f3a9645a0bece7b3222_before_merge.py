    def generic(self, args, kws):
        assert not kws
        if len(args) == 1:
            # One-argument type() -> return the __class__
            classty = self.context.resolve_getattr(args[0], "__class__")
            if classty is not None:
                return signature(classty, *args)