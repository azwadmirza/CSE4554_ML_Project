    def __getitem__(self, item):
        """Allow getting variables as dict keys `settings['KEY']`"""
        value = self.get(item)
        if value is None:
            raise KeyError("{0} does not exists".format(item))
        return value