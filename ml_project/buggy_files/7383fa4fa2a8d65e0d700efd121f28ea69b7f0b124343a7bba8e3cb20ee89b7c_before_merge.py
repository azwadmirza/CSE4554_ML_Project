    def __str__(self):
        if self.exc_class is None:
            return "raise"
        elif self.exc_args is None:
            return "raise %s" % (self.exc_class,)
        else:
            return "raise %s(%s)" % (self.exc_class,
                                     ", ".join(map(repr, self.exc_args)))