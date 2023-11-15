    def impl(cls, item_type, allocated=DEFAULT_ALLOCATED):
        return listobject.new_list(item_type, allocated=allocated)