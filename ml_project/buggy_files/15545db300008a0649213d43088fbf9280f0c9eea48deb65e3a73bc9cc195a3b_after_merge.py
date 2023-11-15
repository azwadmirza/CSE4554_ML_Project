    def __getitem__(self, item):
        """Allow getting variables as dict keys `settings['KEY']`"""
        value = self.get(item, default=empty)
        if value is empty:
            raise KeyError("{0} does not exist".format(item))
        return value