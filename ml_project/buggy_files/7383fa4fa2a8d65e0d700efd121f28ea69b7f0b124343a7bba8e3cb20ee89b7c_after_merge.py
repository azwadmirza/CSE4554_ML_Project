    def __str__(self):
        if self.exc_class is None:
            return "<static> raise"
        elif self.exc_args is None:
            return "<static> raise %s" % (self.exc_class,)
        else:
            return "<static> raise %s(%s)" % (self.exc_class,
                                     ", ".join(map(repr, self.exc_args)))