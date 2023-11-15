    def __setattr__(cls, name, value):
        # Because we can't know whether to try to go to the module
        # or the class, we don't allow setting an attribute after the fact
        raise TypeError("Cannot set attribute")