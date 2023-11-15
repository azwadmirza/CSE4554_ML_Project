    def _maybe_convert_ynames_int(self, ynames):
        # see if they're integers
        issue_warning = False
        msg = ('endog contains values are that not int-like. Uses string '
               'representation of value. Use integer-valued endog to '
               'suppress this warning.')
        for i in ynames:
            try:
                if ynames[i] % 1 == 0:
                    ynames[i] = str(int(ynames[i]))
                else:
                    issue_warning = True
                    ynames[i] = str(ynames[i])
            except TypeError:
                ynames[i] = str(ynames[i])
        if issue_warning:
            import warnings
            warnings.warn(msg, SpecificationWarning)

        return ynames