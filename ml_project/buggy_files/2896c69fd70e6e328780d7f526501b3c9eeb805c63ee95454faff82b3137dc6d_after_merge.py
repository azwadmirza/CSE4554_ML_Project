    def mask(self, cond, other=np.nan, inplace=False, axis=None, level=None,
             errors='raise', try_cast=False, raise_on_error=None):

        if raise_on_error is not None:
            warnings.warn(
                "raise_on_error is deprecated in "
                "favor of errors='raise|ignore'",
                FutureWarning, stacklevel=2)

            if raise_on_error:
                errors = 'raise'
            else:
                errors = 'ignore'

        inplace = validate_bool_kwarg(inplace, 'inplace')
        cond = com._apply_if_callable(cond, self)

        # see gh-21891
        if not hasattr(cond, "__invert__"):
            cond = np.array(cond)

        return self.where(~cond, other=other, inplace=inplace, axis=axis,
                          level=level, try_cast=try_cast,
                          errors=errors)