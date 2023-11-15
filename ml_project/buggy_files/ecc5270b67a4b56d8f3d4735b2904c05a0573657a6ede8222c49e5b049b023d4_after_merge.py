    def __getattr__(self, name):
        """Wrapper that delegates to the actual logger.

        :param name:
        :type name: str
        :return:
        """
        if name not in ADAPTER_MEMBERS:
            return getattr(self.logger, name)

        return getattr(self, ADAPTER_MEMBERS[name])