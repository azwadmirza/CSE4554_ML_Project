    def execute_webhook(self, *, payload, wait=False, file=None, files=None):
        cleanup = None
        if file is not None:
            multipart = {
                'file': (file.filename, file.open_file(), 'application/octet-stream'),
                'payload_json': utils.to_json(payload)
            }
            data = None
            cleanup = file.close
        elif files is not None:
            multipart = {
                'payload_json': utils.to_json(payload)
            }
            for i, file in enumerate(files, start=1):
                multipart['file%i' % i] = (file.filename, file.open_file(), 'application/octet-stream')
            data = None

            def _anon():
                for f in files:
                    f.close()

            cleanup = _anon
        else:
            data = payload
            multipart = None

        url = '%s?wait=%d' % (self._request_url, wait)
        try:
            maybe_coro = self.request('POST', url, multipart=multipart, payload=data)
        finally:
            if cleanup is not None:
                if not asyncio.iscoroutine(maybe_coro):
                    cleanup()
                else:
                    maybe_coro = self._wrap_coroutine_and_cleanup(maybe_coro, cleanup)
        return self.handle_execution_response(maybe_coro, wait=wait)