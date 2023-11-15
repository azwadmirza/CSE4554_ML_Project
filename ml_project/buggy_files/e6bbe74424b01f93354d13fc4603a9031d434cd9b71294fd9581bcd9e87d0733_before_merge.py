    def get_variables(self, sort=None, collapse_same_ident=False):
        """
        Get a list of variables.

        :param str or None sort:    Sort of the variable to get.
        :param collapse_same_ident: Whether variables of the same identifier should be collapsed or not.
        :return:                    A list of variables.
        :rtype:                     list
        """

        variables = [ ]

        if collapse_same_ident:
            raise NotImplementedError()

        for var in self._variables:
            if sort == 'stack' and not isinstance(var, SimStackVariable):
                continue
            if sort == 'reg' and not isinstance(var, SimRegisterVariable):
                continue
            variables.append(var)

        return variables