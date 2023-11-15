    def can_handle(self):
        """
        Validates loader can process environment definition.
        :return: True or False
        """
        # TODO: log information about trying to find the package in binstar.org
        if self.valid_name():
            if self.binstar is None:
                self.msg = "Please install binstar"
                return False
            return self.package is not None and self.valid_package()
        return False