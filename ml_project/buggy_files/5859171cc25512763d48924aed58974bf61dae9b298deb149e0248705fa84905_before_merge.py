    def __call__(self, builder, args, loc=None):
        res = self._imp(self._context, builder, self._sig, args, loc=loc)
        self._context.add_linking_libs(getattr(self, 'libs', ()))
        return res