    def listen(self, *args, **kw):
        once = kw.pop("once", False)
        once_unless_exception = kw.pop("_once_unless_exception", False)
        named = kw.pop("named", False)

        target, identifier, fn = (
            self.dispatch_target,
            self.identifier,
            self._listen_fn,
        )

        dispatch_collection = getattr(target.dispatch, identifier)

        adjusted_fn = dispatch_collection._adjust_fn_spec(fn, named)

        self = self.with_wrapper(adjusted_fn)

        stub_function = getattr(
            self.dispatch_target.dispatch._events, self.identifier
        )
        if hasattr(stub_function, "_sa_warn"):
            stub_function._sa_warn()

        if once or once_unless_exception:
            self.with_wrapper(
                util.only_once(
                    self._listen_fn, retry_on_exception=once_unless_exception
                )
            ).listen(*args, **kw)
        else:
            self.dispatch_target.dispatch._listen(self, *args, **kw)