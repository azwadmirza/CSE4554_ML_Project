    def __truediv__(self, other):
        # there is no true divide if the rhs is not a Number, although it
        # could return the first n elements of an infinite series.
        # It is hard to see where n would come from, though.
        if not isinstance(other, Number) or isinstance(other, bool):
            form = "unsupported types for true division: '%s', '%s'"
            raise TypeError(form % (type(self), type(other)))
        return self.__floordiv__(other)