def make_wrapped_class(local_cls: type, rpyc_wrapper_name: str):
    """
    Replaces given local class in its module with a replacement class
    which has __new__ defined (a dual-nature class).
    This new class is instantiated differently depending on
    whether this is done in remote or local context.

    In local context we effectively get the same behaviour, but in remote
    context the created class is actually of separate type which
    proxies most requests to a remote end.

    Parameters
    ----------
    local_cls: class
        The class to replace with a dual-nature class
    rpyc_wrapper_name: str
        The function *name* to make a proxy class type.
        Note that this is specifically taken as string to not import
        "rpyc_proxy" module in top-level, as it requires RPyC to be
        installed, and not all users of Modin (even in experimental mode)
        need remote context.
    """
    # get a copy of local_cls attributes' dict but skip _very_ special attributes,
    # because copying them to a different type leads to them not working.
    # Python should create new descriptors automatically for us instead.
    namespace = {
        name: value
        for name, value in local_cls.__dict__.items()
        if not isinstance(value, types.GetSetDescriptorType)
    }
    namespace["__real_cls__"] = None
    namespace["__new__"] = None
    # define a new class the same way original was defined but with replaced
    # metaclass and a few more attributes in namespace
    result = RemoteMeta(local_cls.__name__, local_cls.__bases__, namespace)

    def make_new(__class__):
        """
        Define a __new__() with a __class__ that is closure-bound, needed for super() to work
        """

        def __new__(cls, *a, **kw):
            if cls is result and cls.__real_cls__ is not result:
                return cls.__real_cls__(*a, **kw)
            return super().__new__(cls)

        __class__.__new__ = __new__

    make_new(result)
    setattr(sys.modules[local_cls.__module__], local_cls.__name__, result)
    _KNOWN_DUALS[local_cls] = result

    def update_class(_):
        if execution_engine.get() == "Cloudray":
            from . import rpyc_proxy

            result.__real_cls__ = getattr(rpyc_proxy, rpyc_wrapper_name)(result)
        else:
            result.__real_cls__ = result

    execution_engine.subscribe(update_class)