    def detect_poison(self, **kwargs):
        """
        Detect poison.

        :param kwargs: Defence-specific parameters used by child classes.
        :type kwargs: `dict`
        :return: `list` with items identified as poison
        """
        raise NotImplementedError