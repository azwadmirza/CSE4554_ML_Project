    def supportsHotDeployment(cls):
        """
        Whether this batch system supports hot deployment of the user script itself. If it does,
        the :meth:`setUserScript` can be invoked to set the resource object representing the user
        script.

        Note to implementors: If your implementation returns True here, it should also override

        :rtype: bool
        """
        raise NotImplementedError()