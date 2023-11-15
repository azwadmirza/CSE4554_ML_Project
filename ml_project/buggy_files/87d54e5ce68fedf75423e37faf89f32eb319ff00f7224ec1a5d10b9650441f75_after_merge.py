    def __repr__(self):
        if self is self.__singleton:
            return 'masked'
        else:
            # it's a subclass, or something is wrong, make it obvious
            return object.__repr__(self)