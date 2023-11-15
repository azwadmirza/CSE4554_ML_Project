def typedlist_empty(cls, item_type):
    if cls.instance_type is not ListType:
        return

    def impl(cls, item_type):
        return listobject.new_list(item_type)

    return impl