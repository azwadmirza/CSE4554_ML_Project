    def _get_url_data(
            self, url, what=None, msg_status=None, msg_exception=None,
            **kwargs):
        # Compose default messages
        if msg_status is None:
            msg_status = "Cannot get %s" % what

        if msg_exception is None:
            msg_exception = "Retrieval of %s failed." % what

        # Get the URL data
        try:
            response, info = fetch_url(
                self.module, url, timeout=self.timeout, **kwargs)

            if info['status'] != 200:
                self.module.fail_json(msg=msg_status, details=info['msg'])
        except Exception:
            e = get_exception()
            self.module.fail_json(msg=msg_exception, details=e.message)

        return response