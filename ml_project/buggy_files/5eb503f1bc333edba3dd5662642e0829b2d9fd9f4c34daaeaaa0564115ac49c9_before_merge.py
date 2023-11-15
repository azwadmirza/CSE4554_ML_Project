def make_wrapped_class(local_cls: type, rpyc_wrapper_name: str):
    """
    Replaces given local class in its module with a descendant class
    which has __new__ overridden (a dual-nature class).
    This new class is instantiated differently depending o
     whether this is done in remote context or local.

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
    namespace = {
        "__real_cls__": None,
        "__new__": None,
        "__module__": local_cls.__module__,
    }
    result = RemoteMeta(local_cls.__name__, (local_cls,), namespace)

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