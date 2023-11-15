    def subtract_start(self, seconds) -> None:
        """
        Subtracts <seconds> from startts if startts is set.
        :param seconds: Seconds to subtract from starttime
        :return: None (Modifies the object in place)
        """
        if self.startts:
            self.startts = self.startts - seconds