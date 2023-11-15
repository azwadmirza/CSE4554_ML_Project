def _local_find_descriptors(self):
    type_self = type(self)
    gets = set()
    dels = set()
    set_or_del = set()
    sets = set()

    for attr_name in dir(type_self):
        attr = getattr(type_self, attr_name)
        type_attr = type(attr)
        if hasattr(type_attr, '__get__'):
            gets.add(attr_name)
        if hasattr(type_attr, '__delete__'):
            dels.add(attr_name)
            set_or_del.add(attr_name)
        if hasattr(type_attr, '__set__'):
            sets.add(attr_name)

    return (gets, dels, set_or_del, sets)