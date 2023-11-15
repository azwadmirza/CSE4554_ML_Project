    def _apply_to(self, instance, **kwds):
        """
        Applies specified collocation transformation to a modeling instance

        Keyword Arguments:
        nfe           The desired number of finite element points to be
                      included in the discretization.
        ncp           The desired number of collocation points over each
                      finite element.
        wrt           Indicates which ContinuousSet the transformation
                      should be applied to. If this keyword argument is not
                      specified then the same scheme will be applied to all
                      ContinuousSets.
        scheme        Indicates which finite difference method to apply.
                      Options are LAGRANGE-RADAU, LAGRANGE-LEGENDRE, or
                      HERMITE-CUBIC. The default scheme is Lagrange polynomials
                      with Radau roots.
        """

        tmpnfe = kwds.pop('nfe', 10)
        tmpncp = kwds.pop('ncp', 3)
        tmpds = kwds.pop('wrt', None)
        tmpscheme = kwds.pop('scheme', 'LAGRANGE-RADAU')
        self._scheme_name = tmpscheme.upper()

        if tmpds is not None:
            if tmpds.type() is not ContinuousSet:
                raise TypeError("The component specified using the 'wrt' "
                                "keyword must be a continuous set")
            elif 'scheme' in tmpds.get_discretization_info():
                raise ValueError("The discretization scheme '%s' has already "
                                 "been applied to the ContinuousSet '%s'"
                                 % (tmpds.get_discretization_info()['scheme'],
                                    tmpds.name))

        if tmpnfe <= 0:
            raise ValueError(
                "The number of finite elements must be at least 1")
        if tmpncp <= 0:
            raise ValueError(
                "The number of collocation points must be at least 1")

        if None in self._nfe:
            raise ValueError(
                "A general discretization scheme has already been applied to "
                "to every differential set in the model. If you would like to "
                "specify a specific discretization scheme for one of the "
                "differential sets you must discretize each differential set "
                "individually. If you would like to apply a different "
                "discretization scheme to all differential sets you must "
                "declare a new transformation object")

        if len(self._nfe) == 0 and tmpds is None:
            # Same discretization on all differentialsets
            self._nfe[None] = tmpnfe
            self._ncp[None] = tmpncp
            currentds = None
        else:
            self._nfe[tmpds.name] = tmpnfe
            self._ncp[tmpds.name] = tmpncp
            currentds = tmpds.name

        self._scheme = self.all_schemes.get(self._scheme_name, None)
        if self._scheme is None:
            raise ValueError("Unknown collocation scheme '%s' specified using "
                             "the 'scheme' keyword. Valid schemes are "
                             "'LAGRANGE-RADAU', 'LAGRANGE-LEGENDRE', and "
                             "'HERMITE-CUBIC'" % tmpscheme)

        if self._scheme_name == 'LAGRANGE-RADAU':
            self._get_radau_constants(currentds)
        elif self._scheme_name == 'LAGRANGE-LEGENDRE':
            self._get_legendre_constants(currentds)

        self._transformBlock(instance, currentds)

        return instance