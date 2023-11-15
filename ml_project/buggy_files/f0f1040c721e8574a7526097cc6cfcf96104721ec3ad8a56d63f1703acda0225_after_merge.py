    def _parse_arg(self, lsttype, meminfo=None, allocated=DEFAULT_ALLOCATED):
        if not isinstance(lsttype, ListType):
            raise TypeError('*lsttype* must be a ListType')

        if meminfo is not None:
            opaque = meminfo
        else:
            opaque = _make_list(lsttype.item_type, allocated=allocated)
        return lsttype, opaque