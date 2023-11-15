def _local_find_descriptors(self):
    type_self = type(self)
    gets = set()
    dels = set()
    set_or_del = set()
    sets = set()
    mro = list(type_self.mro())

    for attr_name in dir(type_self):
        # Conventionally, descriptors when called on a class
        # return themself, but not all do. Notable exceptions are
        # in the zope.interface package, where things like __provides__
        # return other class attributes. So we can't use getattr, and instead
        # walk up the dicts
        for base in mro:
            if attr_name in base.__dict__:
                attr = base.__dict__[attr_name]
                break
        else:
            raise AttributeError(attr_name)

        type_attr = type(attr)
        if hasattr(type_attr, '__get__'):
            gets.add(attr_name)
        if hasattr(type_attr, '__delete__'):
            dels.add(attr_name)
            set_or_del.add(attr_name)
        if hasattr(type_attr, '__set__'):
            sets.add(attr_name)

    return (gets, dels, set_or_del, sets)