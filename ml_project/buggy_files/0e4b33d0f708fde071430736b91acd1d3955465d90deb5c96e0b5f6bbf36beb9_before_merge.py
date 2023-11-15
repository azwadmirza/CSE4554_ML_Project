    def _handle_greenlet_exc(self, func, host, *args, **kwargs):
        try:
            self._make_ssh_client(host)
            return func(*args, **kwargs)
        except Exception as ex:
            ex.host = host
            raise ex