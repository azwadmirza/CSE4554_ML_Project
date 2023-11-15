    def __call__(self, *args, **kwargs):
        if not ida_enabled:
            return None
        if _ida is None:
            init_ida_rpc_client()
        if _ida is not None:
            return self.fn(*args, **kwargs)
        return None