def make_proxy_cls(
    remote_cls: netref.BaseNetref,
    origin_cls: type,
    override: type,
    cls_name: str = None,
):
    """
    Makes a new class type which inherits from <origin_cls> (for isinstance() and issubtype()),
    takes methods from <override> as-is and proxy all requests for other members to <remote_cls>.
    Note that origin_cls and remote_cls are assumed to be the same class types, but one is local
    and other is obtained from RPyC.

    Effectively implements subclassing, but without subclassing. This is needed because it is
    impossible to subclass a remote-obtained class, something in the very internals of RPyC bugs out.

    Parameters
    ----------
    remote_cls: netref.BaseNetref
        Type obtained from RPyC connection, expected to mirror origin_cls
    origin_cls: type
        The class to prepare a proxying wrapping for
    override: type
        The mixin providing methods and attributes to overlay on top of remote values and methods.
    cls_name: str, optional
        The name to give to the resulting class.

    Returns
    -------
    type
        New wrapper that takes attributes from override and relays requests to all other
        attributes to remote_cls
    """

    class ProxyMeta(RemoteMeta):
        """
        This metaclass deals with printing a telling repr() to assist in debugging,
        and to actually implement the "subclass without subclassing" thing by
        directly adding references to attributes of "override" and by making proxy methods
        for other functions of origin_cls. Class-level attributes being proxied is managed
        by RemoteMeta parent.

        Do note that we cannot do the same for certain special members like __getitem__
        because CPython for optimization doesn't do a lookup of "type(obj).__getitem__(foo)" when
        "obj[foo]" is called, but it effectively does "type(obj).__dict__['__getitem__'](foo)"
        (but even without checking for __dict__), so all present methods must be declared
        beforehand.
        """

        def __repr__(self):
            return f"<proxy for {origin_cls.__module__}.{origin_cls.__name__}:{cls_name or origin_cls.__name__}>"

        def __prepare__(*args, **kw):
            """
            Cooks the __dict__ of the type being constructed. Takes attributes from <override> as is
            and adds proxying wrappers for other attributes of <origin_cls>.
            This "manual inheritance" is needed for RemoteMeta.__getattribute__ which first looks into
            type(obj).__dict__ (EXCLUDING parent classes) and then goes to proxy type.
            """
            namespace = type.__prepare__(*args, **kw)
            namespace["__remote_methods__"] = {}

            # try computing overridden differently to allow subclassing one override from another
            no_override = set(_NO_OVERRIDE)
            for base in override.__mro__:
                if base == object:
                    continue
                for attr_name, attr_value in base.__dict__.items():
                    if (
                        attr_name not in namespace
                        and attr_name not in no_override
                        and getattr(object, attr_name, None) != attr_value
                    ):
                        namespace[
                            attr_name
                        ] = attr_value  # force-inherit an attribute manually
                        no_override.add(attr_name)

            for base in origin_cls.__mro__:
                if base == object:
                    continue
                # try unwrapping a dual-nature class first
                while True:
                    try:
                        sub_base = object.__getattribute__(base, "__real_cls__")
                    except AttributeError:
                        break
                    if sub_base is base:
                        break
                    base = sub_base
                for name, entry in base.__dict__.items():
                    if (
                        name not in namespace
                        and name not in no_override
                        and isinstance(entry, types.FunctionType)
                    ):

                        def method(_self, *_args, __method_name__=name, **_kw):
                            try:
                                remote = _self.__remote_methods__[__method_name__]
                            except KeyError:
                                # use remote_cls.__getattr__ to force RPyC return us
                                # a proxy for remote method call instead of its local wrapper
                                _self.__remote_methods__[
                                    __method_name__
                                ] = remote = remote_cls.__getattr__(__method_name__)
                            return remote(_self.__remote_end__, *_args, **_kw)

                        method.__name__ = name
                        namespace[name] = method
            return namespace

    class Wrapper(override, origin_cls, metaclass=ProxyMeta):
        """
        Subclass origin_cls replacing attributes with what is defined in override while
        relaying requests for all other attributes to remote_cls.
        """

        __name__ = cls_name or origin_cls.__name__
        __wrapper_remote__ = remote_cls

        def __init__(self, *a, __remote_end__=None, **kw):
            if __remote_end__ is None:
                __remote_end__ = remote_cls(*a, **kw)
            while True:
                # unwrap the object if it's a wrapper
                try:
                    __remote_end__ = object.__getattribute__(
                        __remote_end__, "__remote_end__"
                    )
                except AttributeError:
                    break
            object.__setattr__(self, "__remote_end__", __remote_end__)

        @classmethod
        def from_remote_end(cls, remote_inst):
            return cls(__remote_end__=remote_inst)

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

        if override.__setattr__ == object.__setattr__:
            # no custom attribute setting, define our own relaying to remote end
            def __setattr__(self, name, value):
                if name not in _PROXY_LOCAL_ATTRS:
                    setattr(self.__remote_end__, name, value)
                else:
                    object.__setattr__(self, name, value)

        if override.__delattr__ == object.__delattr__:
            # no custom __delattr__, define our own
            def __delattr__(self, name):
                if name not in _PROXY_LOCAL_ATTRS:
                    delattr(self.__remote_end__, name)

    return Wrapper