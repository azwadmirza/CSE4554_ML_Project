    def write_fh(self, fh, key: str, md5: bytes,
                 metadata: Optional[Dict[str, Any]] = None,
                 size: Optional[int] = None):
        '''Write data from byte stream *fh* into *key*.

        *fh* must be seekable. If *size* is None, *fh* must also implement
        `fh.fileno()` so that the size can be determined through `os.fstat`.

        *md5* must be the (binary) md5 checksum of the data.
        '''

        metadata = json.dumps({
            'metadata': _wrap_user_meta(metadata if metadata else {}),
            'md5Hash': b64encode(md5).decode(),
            'name': self.prefix + key,
        })

        # Google Storage uses Content-Length to read the object data, so we
        # don't have to worry about the boundary occurring in the object data.
        boundary = 'foo_bar_baz'
        headers = CaseInsensitiveDict()
        headers['Content-Type'] = 'multipart/related; boundary=%s' % boundary

        body_prefix = '\n'.join(('--' + boundary,
                                 'Content-Type: application/json; charset=UTF-8',
                                 '', metadata,
                                 '--' + boundary,
                                 'Content-Type: application/octet-stream',
                                 '', '')).encode()
        body_suffix = ('\n--%s--\n' % boundary).encode()

        body_size = len(body_prefix) + len(body_suffix)
        if size is not None:
            body_size += size
        else:
            body_size += os.fstat(fh.fileno()).st_size

        path = '/upload/storage/v1/b/%s/o' % (
            urllib.parse.quote(self.bucket_name, safe=''),)
        query_string = {'uploadType': 'multipart'}
        try:
            resp = self._do_request('POST', path, query_string=query_string,
                                    headers=headers, body=BodyFollowing(body_size))
        except RequestError as exc:
            exc = _map_request_error(exc, key)
            if exc:
                raise exc
            raise

        assert resp.status == 100
        fh.seek(0)

        md5_run = hashlib.md5()
        try:
            self.conn.write(body_prefix)
            while True:
                buf = fh.read(BUFSIZE)
                if not buf:
                    break
                self.conn.write(buf)
                md5_run.update(buf)
            self.conn.write(body_suffix)
        except ConnectionClosed:
            # Server closed connection while we were writing body data -
            # but we may still be able to read an error response
            try:
                resp = self.conn.read_response()
            except ConnectionClosed: # No server response available
                pass
            else:
                if resp.status >= 400: # Got error response
                    return resp
                    log.warning('Server broke connection during upload, but signaled '
                                '%d %s', resp.status, resp.reason)
            # Re-raise first ConnectionClosed exception
            raise

        if md5_run.digest() != md5:
            raise ValueError('md5 passed to write_fd does not match fd data')

        resp = self.conn.read_response()
        if resp.status != 200:
            exc = self._parse_error_response(resp)
            # If we're really unlucky, then the token has expired while we
            # were uploading data.
            if exc.message == 'Invalid Credentials':
                raise AccessTokenExpired()
            raise _map_request_error(exc, key) or exc
        self._parse_json_response(resp)