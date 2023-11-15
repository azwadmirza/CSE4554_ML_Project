    def __getitem__(self, item):
        ret = super(HyList, self).__getitem__(item)

        if isinstance(item, slice):
            return self.__class__(ret)

        return ret