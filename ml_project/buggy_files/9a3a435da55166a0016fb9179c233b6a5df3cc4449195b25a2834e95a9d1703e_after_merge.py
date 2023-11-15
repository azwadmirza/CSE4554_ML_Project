        def __getattribute__(self, name):
            """
            Implement "default" resolution order to override whatever __getattribute__
            a parent being wrapped may have defined, but only look up on own __dict__
            without looking into ancestors' ones, because we copy them in __prepare__.

            Effectively, any attributes not currently known to Wrapper (i.e. not defined here
            or in override class) will be retrieved from the remote end.

            Algorithm (mimicking default Python behaviour):
            1) check if type(self).__dict__[name] exists and is a get/set data descriptor
            2) check if self.__dict__[name] exists
            3) check if type(self).__dict__[name] is a non-data descriptor
            4) check if type(self).__dict__[name] exists
            5) pass through to remote end
            """
            if name == "__class__":
                return object.__getattribute__(self, "__class__")
            dct = object.__getattribute__(self, "__dict__")
            if name == "__dict__":
                return dct
            cls_dct = object.__getattribute__(type(self), "__dict__")
            try:
                cls_attr, has_cls_attr = cls_dct[name], True
            except KeyError:
                has_cls_attr = False
            else:
                oget = None
                try:
                    oget = object.__getattribute__(cls_attr, "__get__")
                    object.__getattribute__(cls_attr, "__set__")
                except AttributeError:
                    pass  # not a get/set data descriptor, go next
                else:
                    return oget(self, type(self))
            # type(self).name is not a get/set data descriptor
            try:
                return dct[name]
            except KeyError:
                # instance doesn't have an attribute
                if has_cls_attr:
                    # type(self) has this attribute, but it's not a get/set descriptor
                    if oget:
                        # this attribute is a get data descriptor
                        return oget(self, type(self))
                    return cls_attr  # not a data descriptor whatsoever

            # this instance/class does not have this attribute, pass it through to remote end
            return getattr(dct["__remote_end__"], name)