    def build(self, path=None, tag=None, quiet=False, fileobj=None,
              nocache=False, rm=False, stream=False, timeout=None):
        remote = context = headers = None
        if path is None and fileobj is None:
            raise Exception("Either path or fileobj needs to be provided.")

        if fileobj is not None:
            context = utils.mkbuildcontext(fileobj)
        elif path.startswith(('http://', 'https://', 'git://', 'github.com/')):
            remote = path
        else:
            context = utils.tar(path)

        u = self._url('/build')
        params = {
            't': tag,
            'remote': remote,
            'q': quiet,
            'nocache': nocache,
            'rm': rm
        }
        if context is not None:
            headers = {'Content-Type': 'application/tar'}

        response = self._post(
            u,
            data=context,
            params=params,
            headers=headers,
            stream=stream,
            timeout=timeout,
        )

        if context is not None:
            context.close()

        if stream or utils.compare_version('1.8', self._version) >= 0:
            return self._stream_helper(response)
        else:
            output = self._result(response)
            srch = r'Successfully built ([0-9a-f]+)'
            match = re.search(srch, output)
            if not match:
                return None, output
            return match.group(1), output