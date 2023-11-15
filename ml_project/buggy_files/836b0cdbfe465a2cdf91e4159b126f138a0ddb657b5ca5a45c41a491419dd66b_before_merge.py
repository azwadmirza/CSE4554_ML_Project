    def supportsHotDeployment(cls):
        """
        Whether this batch system supports hot deployment of the user script itself. If it does,
        the __init__ method will have to accept an optional parameter in addition to the declared
        ones: userScript. It will be an instance of toil.common.HotDeployedResource that
        represents the user script.

        :rtype: bool
        """
        raise NotImplementedError()