def concretize(maybe_stub):
    if isinstance(maybe_stub, StubMethodCall):
        obj = concretize(maybe_stub.obj)
        method = getattr(obj, maybe_stub.method_name)
        args = concretize(maybe_stub.args)
        kwargs = concretize(maybe_stub.kwargs)
        return method(*args, **kwargs)
    elif isinstance(maybe_stub, StubClass):
        return maybe_stub.proxy_class
    elif isinstance(maybe_stub, StubAttr):
        obj = concretize(maybe_stub.obj)
        attr_name = maybe_stub.attr_name
        attr_val = getattr(obj, attr_name)
        return concretize(attr_val)
    elif isinstance(maybe_stub, StubObject):
        if not hasattr(maybe_stub, "__stub_cache"):
            args = concretize(maybe_stub.args)
            kwargs = concretize(maybe_stub.kwargs)
            try:
                maybe_stub.__stub_cache = maybe_stub.proxy_class(
                    *args, **kwargs)
            except Exception as e:
                print(
                    ("Error while instantiating %s" % maybe_stub.proxy_class))
                import traceback
                traceback.print_exc()
        ret = maybe_stub.__stub_cache
        return ret
    elif isinstance(maybe_stub, dict):
        # make sure that there's no hidden caveat
        ret = dict()
        for k, v in maybe_stub.items():
            ret[concretize(k)] = concretize(v)
        return ret
    elif isinstance(maybe_stub, (list, tuple)):
        return maybe_stub.__class__(list(map(concretize, maybe_stub)))
    else:
        return maybe_stub