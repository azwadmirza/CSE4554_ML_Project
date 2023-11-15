    def _handle_greenlet_exc(self, func, host, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            ex.host = host
            raise ex