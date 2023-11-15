    def __array_finalize__(self, obj):
        if self.__singleton is None:
            # this handles the `.view` in __new__, which we want to copy across
            # properties normally
            return super(MaskedConstant, self).__array_finalize__(obj)
        elif self is self.__singleton:
            # not clear how this can happen, play it safe
            pass
        else:
            # everywhere else, we want to downcast to MaskedArray, to prevent a
            # duplicate maskedconstant.
            self.__class__ = MaskedArray
            MaskedArray.__array_finalize__(self, obj)