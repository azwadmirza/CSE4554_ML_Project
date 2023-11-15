    def _break_constant(self, const):
        """
        Break down constant exception.
        """
        if isinstance(const, tuple): # it's a tuple(exception class, args)
            if not self._is_exception_type(const[0]):
                raise NotImplementedError("unsupported exception constant %r"
                                          % (const[0],))
            return const[0], tuple(const[1])
        elif self._is_exception_type(const):
            return const, None
        else:
            raise NotImplementedError("unsupported exception constant %r"
                                      % (const,))