    def _break_constant(self, const, loc):
        """
        Break down constant exception.
        """
        if isinstance(const, tuple): # it's a tuple(exception class, args)
            if not self._is_exception_type(const[0]):
                msg = "Encountered unsupported exception constant %r"
                raise errors.UnsupportedError(msg % (const[0],), loc)
            return const[0], tuple(const[1])
        elif self._is_exception_type(const):
            return const, None
        else:
            if isinstance(const, str):
                msg = ("Directly raising a string constant as an exception is "
                       "not supported.")
            else:
                msg = "Encountered unsupported constant type used for exception"
            raise errors.UnsupportedError(msg, loc)