    def _break_constant(self, interp, const):
        """
        Break down constant exception.
        """
        if isinstance(const, BaseException):
            return const.__class__, const.args
        elif self._is_exception_type(const):
            return const, None
        else:
            raise NotImplementedError("unsupported exception constant %r"
                                      % (const,))