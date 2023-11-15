    def generic(self, args, kws):
        arg, = args
        if self.is_accepted_type(arg):
            return signature(types.none, *args)