def typedlist_empty(cls, item_type, allocated=DEFAULT_ALLOCATED):
    if cls.instance_type is not ListType:
        return

    def impl(cls, item_type, allocated=DEFAULT_ALLOCATED):
        return listobject.new_list(item_type, allocated=allocated)

    return impl