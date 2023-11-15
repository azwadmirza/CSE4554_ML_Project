    def supportsHotDeployment(cls):
        """
        Whether this batch system supports hot deployment of the user script and toil itself. If
        it does, the __init__ method will have to accept two optional parameters in addition to
        the declared ones: userScript and toilDistribution. Both will be instances of
        toil.common.HotDeployedResource that represent the user script and a source tarball (
        sdist) of toil respectively.

        :rtype: bool
        """
        raise NotImplementedError()