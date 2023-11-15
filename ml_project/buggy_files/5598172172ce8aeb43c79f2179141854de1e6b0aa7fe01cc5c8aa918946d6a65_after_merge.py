    def can_handle(self):
        """
        Validates loader can process environment definition.
        :return: True or False
        """
        # TODO: log information about trying to find the package in binstar.org
        if self.valid_name():
            if self.binstar is None:
                self.msg = ("Anaconda Client is required to interact with anaconda.org or an "
                            "Anaconda API. Please run `conda install anaconda-client`.")
                return False
            return self.package is not None and self.valid_package()
        return False