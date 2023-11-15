    def execute_webhook(self, *, payload, wait=False, file=None, files=None):
        if file is not None:
            multipart = {
                'file': file,
                'payload_json': utils.to_json(payload)
            }
            data = None
        elif files is not None:
            multipart = {
                'payload_json': utils.to_json(payload)
            }
            for i, file in enumerate(files, start=1):
                multipart['file%i' % i] = file
            data = None
        else:
            data = payload
            multipart = None

        url = '%s?wait=%d' % (self._request_url, wait)
        maybe_coro = self.request('POST', url, multipart=multipart, payload=data)
        return self.handle_execution_response(maybe_coro, wait=wait)