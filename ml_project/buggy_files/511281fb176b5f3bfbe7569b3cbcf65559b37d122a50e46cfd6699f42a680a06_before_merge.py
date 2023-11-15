    def __init__(self, connection, base, index=(), data=None):
        """Make new QuotedRPath"""
        super().__init__(connection, base, index, data)
        self.quoted_index = tuple(map(quote, self.index))
        # we need to recalculate path and data on the basis of
        # quoted_index (parent class does it on the basis of index)
        if base is not None:
            self.path = self.path_join(self.base, *self.quoted_index)
            if data is None:
                self.setdata()