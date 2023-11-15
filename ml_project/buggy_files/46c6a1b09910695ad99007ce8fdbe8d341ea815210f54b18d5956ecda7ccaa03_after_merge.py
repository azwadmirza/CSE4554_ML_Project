    def _apply_to(self, instance, **kwds):
        """
        Applies the transformation to a modeling instance

        Keyword Arguments:
        nfe           The desired number of finite element points to be
                      included in the discretization.
        wrt           Indicates which ContinuousSet the transformation
                      should be applied to. If this keyword argument is not
                      specified then the same scheme will be applied to all
                      ContinuousSets.
        scheme        Indicates which finite difference method to apply.
                      Options are BACKWARD, CENTRAL, or FORWARD. The default
                      scheme is the backward difference method
        """

        tmpnfe = kwds.pop('nfe', 10)
        tmpds = kwds.pop('wrt', None)
        tmpscheme = kwds.pop('scheme', 'BACKWARD')
        self._scheme_name = tmpscheme.upper()

        if tmpds is not None:
            if tmpds.type() is not ContinuousSet:
                raise TypeError("The component specified using the 'wrt' "
                                "keyword must be a continuous set")
            elif 'scheme' in tmpds.get_discretization_info():
                raise ValueError("The discretization scheme '%s' has already "
                                 "been applied to the ContinuousSet '%s'" %
                                 (tmpds.get_discretization_info()['scheme'],
                                  tmpds.name))

        if None in self._nfe:
            raise ValueError(
                "A general discretization scheme has already been applied to "
                "to every continuous set in the model. If you would like to "
                "apply a different discretization scheme to each continuous "
                "set, you must declare a new transformation object")

        if len(self._nfe) == 0 and tmpds is None:
            # Same discretization on all differentialsets
            self._nfe[None] = tmpnfe
            currentds = None
        else:
            self._nfe[tmpds.name] = tmpnfe
            currentds = tmpds.name

        self._scheme = self.all_schemes.get(self._scheme_name, None)
        if self._scheme is None:
            raise ValueError("Unknown finite difference scheme '%s' specified "
                             "using the 'scheme' keyword. Valid schemes are "
                             "'BACKWARD', 'CENTRAL', and 'FORWARD'" %
                             tmpscheme)

        self._transformBlock(instance, currentds)

        return instance